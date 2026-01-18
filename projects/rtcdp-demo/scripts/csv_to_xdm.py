#!/usr/bin/env python3
"""
CSV to XDM JSON 변환 스크립트

samples/data/ 폴더의 CSV 파일들을 AEP에 수집 가능한 XDM JSON 형식으로 변환합니다.

사용법:
    python csv_to_xdm.py

출력:
    schemas/ 폴더에 XDM JSON 파일 생성
    - customer-data.json
    - order-data.json
    - web-events-data.json
    - product-data.json
"""

import csv
import json
import os
from datetime import datetime
from pathlib import Path


# 경로 설정
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DATA_DIR = PROJECT_DIR.parent.parent / "samples" / "data"
OUTPUT_DIR = PROJECT_DIR / "schemas"


def convert_customer_to_xdm(csv_path: Path) -> list:
    """
    customer.csv를 XDM Profile JSON으로 변환

    CSV 컬럼:
        customer_id, first_name, last_name, email, phone,
        city, country, loyalty_points, join_date, membership_status

    XDM 매핑:
        - customer_id → _rtcdpDemo.customerId (Primary Identity)
        - email → personalEmail.address
        - phone → mobilePhone.number
        - first_name/last_name → person.name
        - city/country → _rtcdpDemo.address
        - loyalty_points → _rtcdpDemo.loyaltyPoints
        - membership_status → _rtcdpDemo.membershipStatus
        - join_date → _rtcdpDemo.joinDate
    """
    records = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 날짜 형식 변환 (YYYY-MM-DD → ISO 8601)
            join_date = row['join_date']
            if join_date and 'T' not in join_date:
                join_date = f"{join_date}T00:00:00Z"

            xdm_record = {
                "person": {
                    "name": {
                        "firstName": row['first_name'],
                        "lastName": row['last_name']
                    }
                },
                "personalEmail": {
                    "address": row['email']
                },
                "mobilePhone": {
                    "number": row['phone']
                },
                "_rtcdpDemo": {
                    "customerId": row['customer_id'],
                    "loyaltyPoints": int(row['loyalty_points']),
                    "membershipStatus": row['membership_status'],
                    "joinDate": join_date,
                    "address": {
                        "city": row['city'],
                        "country": row['country']
                    }
                }
            }
            records.append(xdm_record)

    return records


def convert_orders_to_xdm(orders_csv: Path, items_csv: Path) -> list:
    """
    order.csv + order_item.csv를 XDM Experience Event JSON으로 변환

    order.csv 컬럼:
        order_id, customer_id, order_date, total_amount, status,
        payment_method, shipping_address

    order_item.csv 컬럼:
        order_id, product_id, quantity, unit_price, total_price

    XDM 매핑:
        - order_date → timestamp
        - customer_id → identityMap.CustomerID
        - order_id → commerce.order.purchaseID
        - total_amount → commerce.order.priceTotal
        - product_id → productListItems[].SKU
        - quantity → productListItems[].quantity
        - total_price → productListItems[].priceTotal
        - status → _rtcdpDemo.orderStatus
        - payment_method → _rtcdpDemo.paymentMethod
    """
    # order_item을 order_id로 그룹핑
    items_by_order = {}
    with open(items_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            order_id = row['order_id']
            if order_id not in items_by_order:
                items_by_order[order_id] = []
            items_by_order[order_id].append({
                "SKU": row['product_id'],
                "quantity": int(row['quantity']),
                "priceTotal": float(row['total_price']),
                "currencyCode": "USD"
            })

    # 주문 레코드 생성
    records = []
    with open(orders_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            order_id = row['order_id']

            # 날짜 형식 변환
            order_date = row['order_date']
            if order_date and 'T' not in order_date:
                order_date = f"{order_date}T00:00:00Z"

            xdm_record = {
                "_id": f"commerce-{order_id}",
                "timestamp": order_date,
                "eventType": "commerce.purchases",
                "identityMap": {
                    "CustomerID": [{
                        "id": row['customer_id'],
                        "primary": True,
                        "authenticatedState": "authenticated"
                    }]
                },
                "commerce": {
                    "order": {
                        "purchaseID": order_id,
                        "priceTotal": float(row['total_amount']),
                        "currencyCode": "USD"
                    },
                    "purchases": {
                        "value": 1
                    }
                },
                "productListItems": items_by_order.get(order_id, []),
                "_rtcdpDemo": {
                    "orderId": order_id,
                    "orderStatus": row['status'],
                    "paymentMethod": row['payment_method'],
                    "shippingAddress": row['shipping_address']
                }
            }
            records.append(xdm_record)

    return records


def convert_web_events_to_xdm(csv_path: Path) -> list:
    """
    sample-web-events.csv를 XDM Experience Event JSON으로 변환

    CSV 컬럼:
        eventId, timestamp, personId, eventType, pageUrl, pageName,
        referrerUrl, browser, device, browserWidth, browserHeight

    XDM 매핑:
        - eventId → _id, _rtcdpDemo.eventId
        - timestamp → timestamp
        - personId → identityMap.ECID
        - eventType → eventType, _rtcdpDemo.eventType
        - pageUrl → web.webPageDetails.URL
        - pageName → web.webPageDetails.name
        - referrerUrl → web.webReferrer.URL
        - device → device.type
        - browserWidth/Height → environment.browserDetails
    """
    records = []

    # eventType 매핑
    event_type_map = {
        "page_view": "web.webpagedetails.pageViews",
        "add_to_cart": "commerce.productListAdds",
        "purchase": "commerce.purchases",
        "product_view": "commerce.productViews"
    }

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 빈 행 스킵
            if not row.get('eventId'):
                continue

            # eventType 변환
            raw_event_type = row['eventType']
            xdm_event_type = event_type_map.get(raw_event_type, f"web.{raw_event_type}")

            xdm_record = {
                "_id": f"web-{row['eventId']}",
                "timestamp": row['timestamp'],
                "eventType": xdm_event_type,
                "identityMap": {
                    "ECID": [{
                        "id": row['personId'],
                        "primary": True,
                        "authenticatedState": "ambiguous"
                    }]
                },
                "web": {
                    "webPageDetails": {
                        "URL": row['pageUrl'],
                        "name": row['pageName'],
                        "pageViews": {
                            "value": 1 if raw_event_type == "page_view" else 0
                        }
                    }
                },
                "device": {
                    "type": row['device']
                },
                "_rtcdpDemo": {
                    "eventId": row['eventId'],
                    "eventType": raw_event_type
                }
            }

            # 리퍼러 URL (있는 경우에만)
            if row.get('referrerUrl'):
                xdm_record["web"]["webReferrer"] = {
                    "URL": row['referrerUrl']
                }

            # 브라우저 뷰포트 정보 (있는 경우에만)
            if row.get('browserWidth') and row.get('browserHeight'):
                xdm_record["environment"] = {
                    "browserDetails": {
                        "viewportWidth": int(row['browserWidth']),
                        "viewportHeight": int(row['browserHeight'])
                    }
                }

            records.append(xdm_record)

    return records


def convert_products_to_xdm(csv_path: Path) -> list:
    """
    product.csv를 XDM Lookup JSON으로 변환

    CSV 컬럼:
        product_id, name, category, price, stock_quantity, description, brand

    XDM 매핑:
        - product_id → _rtcdpDemo.productId
        - name → _rtcdpDemo.productName
        - category → _rtcdpDemo.category
        - price → _rtcdpDemo.price
        - stock_quantity → _rtcdpDemo.stockQuantity
        - description → _rtcdpDemo.description
        - brand → _rtcdpDemo.brand
    """
    records = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            xdm_record = {
                "_rtcdpDemo": {
                    "productId": row['product_id'],
                    "productName": row['name'],
                    "category": row['category'],
                    "price": float(row['price']),
                    "stockQuantity": int(row['stock_quantity']),
                    "description": row['description'],
                    "brand": row['brand'],
                    "isActive": True,
                    "createdAt": datetime.now().isoformat() + "Z"
                }
            }
            records.append(xdm_record)

    return records


def save_json(data: list, output_path: Path, pretty: bool = True):
    """JSON 파일 저장"""
    with open(output_path, 'w', encoding='utf-8') as f:
        if pretty:
            json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            json.dump(data, f, ensure_ascii=False)
    print(f"  -> {output_path.name}: {len(data)} records")


def main():
    """Main execution function"""
    print("=" * 60)
    print("CSV to XDM JSON Conversion")
    print("=" * 60)
    print(f"Data source: {DATA_DIR}")
    print(f"Output folder: {OUTPUT_DIR}")
    print()

    # Create output folder
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Customer Profiles
    print("[1/4] Converting Customer Profiles...")
    customer_csv = DATA_DIR / "customer.csv"
    if customer_csv.exists():
        customers = convert_customer_to_xdm(customer_csv)
        save_json(customers, OUTPUT_DIR / "customer-data.json")
    else:
        print(f"  [!] File not found: {customer_csv}")

    # 2. Commerce Events (Orders)
    print("[2/4] Converting Commerce Events...")
    orders_csv = DATA_DIR / "order.csv"
    items_csv = DATA_DIR / "order_item.csv"
    if orders_csv.exists() and items_csv.exists():
        orders = convert_orders_to_xdm(orders_csv, items_csv)
        save_json(orders, OUTPUT_DIR / "order-data.json")
    else:
        print("  [!] File not found: order.csv or order_item.csv")

    # 3. Web Events
    print("[3/4] Converting Web Events...")
    web_events_csv = DATA_DIR / "sample-web-events.csv"
    if web_events_csv.exists():
        web_events = convert_web_events_to_xdm(web_events_csv)
        save_json(web_events, OUTPUT_DIR / "web-events-data.json")
    else:
        print(f"  [!] File not found: {web_events_csv}")

    # 4. Products (Lookup)
    print("[4/4] Converting Products...")
    products_csv = DATA_DIR / "product.csv"
    if products_csv.exists():
        products = convert_products_to_xdm(products_csv)
        save_json(products, OUTPUT_DIR / "product-data.json")
    else:
        print(f"  [!] File not found: {products_csv}")

    print()
    print("=" * 60)
    print("Conversion Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Create schemas in AEP UI")
    print("2. Create datasets")
    print("3. Upload generated JSON files to datasets")


if __name__ == "__main__":
    main()
