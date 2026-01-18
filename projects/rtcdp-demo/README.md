# RTCDP Demo Project

Real-Time Customer Data Platform(RTCDP) 데모 프로젝트입니다. 샘플 데이터를 활용하여 AEP의 핵심 기능을 실습합니다.

## 프로젝트 개요

이커머스 시나리오 기반의 RTCDP 데모로, 고객 프로필 통합부터 세그먼트 활성화까지 전체 워크플로우를 구현합니다.

### 사용 데이터

| 파일 | 설명 | XDM 클래스 |
|------|------|-----------|
| `customer.csv` | 고객 프로필 (10명) | XDM Individual Profile |
| `order.csv` | 주문 내역 (10건) | XDM Experience Event |
| `order_item.csv` | 주문 상품 상세 | XDM Experience Event |
| `product.csv` | 상품 마스터 (10개) | Lookup Schema |
| `sample-web-events.csv` | 웹 행동 이벤트 | XDM Experience Event |

### 데모 시나리오

**이커머스 고객 통합 플랫폼**
- 고객 프로필 + 구매 이력 + 웹 행동 데이터 통합
- 실시간 고객 세그멘테이션
- 마케팅 채널 활성화

---

## 프로젝트 구조

```
rtcdp-demo/
├── README.md                    # 프로젝트 개요 (현재 문서)
├── docs/                        # Phase별 상세 가이드
│   ├── phase1-schema-design.md  # 스키마 설계
│   ├── phase2-identity.md       # Identity 설정
│   ├── phase3-data-ingestion.md # 데이터 수집
│   ├── phase4-segmentation.md   # 세그먼트 정의
│   ├── phase5-web-demo.md       # 데모 웹사이트
│   └── phase6-activation.md     # Activation
├── schemas/                     # XDM 스키마 정의 (JSON)
│   ├── profile-schema.json
│   ├── commerce-event-schema.json
│   ├── web-event-schema.json
│   └── product-lookup-schema.json
├── scripts/                     # 데이터 변환/수집 스크립트
│   └── csv-to-xdm.py
└── web-demo/                    # Web SDK 데모 페이지
    ├── index.html
    ├── product.html
    └── checkout.html
```

---

## 실행 순서

### Phase 1: 스키마 설계 (1-2일)
AEP에서 데이터를 수집하기 위한 XDM 스키마를 설계합니다.

| 스키마 | 클래스 | 용도 |
|--------|--------|------|
| Customer Profile | XDM Individual Profile | 고객 속성 데이터 |
| Commerce Event | XDM Experience Event | 주문/구매 이벤트 |
| Web Event | XDM Experience Event | 웹 행동 이벤트 |
| Product Lookup | Custom Lookup | 상품 정보 조회 |

**상세 가이드**: [docs/phase1-schema-design.md](docs/phase1-schema-design.md)

---

### Phase 2: Identity 설정 (0.5일)
고객 식별을 위한 Identity Namespace와 Graph 설정을 구성합니다.

| Namespace | Type | 용도 |
|-----------|------|------|
| Email | Email | 기본 식별자, 로그인 ID |
| Phone | Phone | 보조 식별자 |
| CustomerID | Custom | CRM 시스템 ID |
| ECID | Cookie | 웹 브라우저 식별 |

**상세 가이드**: [docs/phase2-identity.md](docs/phase2-identity.md)

---

### Phase 3: 데이터 수집 (1-2일)
샘플 CSV 데이터를 XDM 형식으로 변환하고 AEP에 수집합니다.

**수집 방법**:
- Batch Ingestion: CSV 파일 업로드
- Streaming: Web SDK를 통한 실시간 수집

**상세 가이드**: [docs/phase3-data-ingestion.md](docs/phase3-data-ingestion.md)

---

### Phase 4: 세그먼트 정의 (1일)
비즈니스 시나리오 기반 오디언스 세그먼트를 생성합니다.

| 세그먼트 | 조건 | 평가 방식 |
|----------|------|----------|
| VIP 고객 | membership_status = 'VIP' OR loyalty_points > 2000 | Batch |
| Premium 회원 | membership_status = 'Premium' | Streaming |
| 최근 구매자 | 30일 내 purchase 이벤트 | Streaming |
| 장바구니 이탈 | add_to_cart 후 24시간 내 purchase 없음 | Streaming |
| 비활성 고객 | 90일간 이벤트 없음 | Batch |

**상세 가이드**: [docs/phase4-segmentation.md](docs/phase4-segmentation.md)

---

### Phase 5: 데모 웹사이트 (1-2일)
Web SDK가 통합된 샘플 이커머스 페이지를 구축합니다.

**구현 페이지**:
- `index.html` - 홈페이지 (pageView 이벤트)
- `product.html` - 상품 상세 (productView, addToCart 이벤트)
- `checkout.html` - 결제 (purchase 이벤트)

**상세 가이드**: [docs/phase5-web-demo.md](docs/phase5-web-demo.md)

---

### Phase 6: Activation (0.5-1일)
세그먼트를 외부 채널로 활성화합니다.

**대상 Destination**:
- HTTP API Endpoint (테스트용)
- Google Ads (선택)
- Email Platform (선택)

**상세 가이드**: [docs/phase6-activation.md](docs/phase6-activation.md)

---

## 사전 요구사항

### AEP 환경
- [ ] Adobe Experience Platform 액세스 권한
- [ ] Sandbox 생성 권한 (권장: 전용 개발 Sandbox)
- [ ] Schema, Dataset, Segment 생성 권한

### 개발 환경
- [ ] Node.js v14+ (Web SDK 테스트용)
- [ ] Python 3.8+ (데이터 변환 스크립트용)
- [ ] 웹 브라우저 (Chrome 권장, AEP Debugger 확장 설치)

### API 설정 (선택)
- [ ] Adobe Developer Console 프로젝트
- [ ] API 인증 정보 (Client ID, Secret, Access Token)

---

## 학습 체크리스트

### Phase 1 완료 시
- [ ] XDM 스키마 4개 생성 완료
- [ ] Field Group 구성 이해
- [ ] Primary Identity 설정 완료
- [ ] Schema가 Profile에 활성화됨

### Phase 2 완료 시
- [ ] Identity Namespace 3개 생성
- [ ] Identity Graph 연결 관계 이해

### Phase 3 완료 시
- [ ] Dataset 4개 생성 및 데이터 수집 완료
- [ ] Profile에서 통합된 고객 데이터 확인

### Phase 4 완료 시
- [ ] 세그먼트 5개 생성
- [ ] 각 세그먼트 population 확인

### Phase 5 완료 시
- [ ] Web SDK 이벤트 수집 동작 확인
- [ ] AEP Debugger로 이벤트 검증

### Phase 6 완료 시
- [ ] Destination 연결 완료
- [ ] 세그먼트 활성화 데이터 흐름 확인

---

## 샘플 데이터 위치

```
adobe-aep-learn/samples/data/
├── customer.csv           # 고객 프로필
├── order.csv              # 주문 내역
├── order_item.csv         # 주문 상품
├── product.csv            # 상품 마스터
├── category.csv           # 카테고리
└── sample-web-events.csv  # 웹 이벤트
```

---

## 최근 업데이트

### 2026-01-18: Identity Descriptor 표준화

**CRITICAL 이슈 수정**: Lookup 스키마의 Identity 설정을 AEP 표준 API 패턴으로 변경

**변경 사항**:
1. `product-lookup-schema.json`에서 비표준 `meta:usesIdentity` 속성 제거
2. `aep_schema_builder.py`에 Identity Descriptor API 기능 추가:
   - `create_identity_namespace()`: ProductID Namespace 생성 (idType: NON_PEOPLE)
   - `create_identity_descriptor()`: Identity Descriptor 생성
   - `setup_lookup_identity()`: Lookup 스키마용 통합 설정
3. `create_schema()` 워크플로우에 자동 Identity 설정 통합

**상세 문서**: [IDENTITY_DESCRIPTOR_FIX.md](IDENTITY_DESCRIPTOR_FIX.md)

**검증 스크립트**: `scripts/test_identity_methods.py`

---

## 참고 자료

- [XDM 스키마 문서](https://experienceleague.adobe.com/docs/experience-platform/xdm/home.html)
- [Identity Service 문서](https://experienceleague.adobe.com/docs/experience-platform/identity/home.html)
- [Segmentation 문서](https://experienceleague.adobe.com/docs/experience-platform/segmentation/home.html)
- [Web SDK 문서](https://experienceleague.adobe.com/docs/experience-platform/web-sdk/home.html)
- [Destinations 문서](https://experienceleague.adobe.com/docs/experience-platform/destinations/home.html)
