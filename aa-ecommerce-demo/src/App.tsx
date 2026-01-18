import { useState, useEffect, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'
import { ShoppingCart, Plus, Minus, Trash2, CreditCard, Package, Search, Tag, Eye, CheckCircle2 } from 'lucide-react'

// Types
interface Product {
  id: string
  sku: string
  name: string
  category: string
  price: number
  originalPrice?: number
  image: string
  description: string
  rating: number
  reviews: number
}

interface CartItem extends Product {
  quantity: number
}

interface AnalyticsEvent {
  timestamp: string
  eventType: string
  details: string
  rawData: Record<string, unknown>
}

// Sample Products
const products: Product[] = [
  {
    id: '1', sku: 'SHOE-001', name: '프리미엄 러닝화', category: '신발',
    price: 159000, originalPrice: 199000, image: '👟',
    description: '가벼운 쿠셔닝과 통기성이 뛰어난 프리미엄 러닝화입니다.',
    rating: 4.8, reviews: 234
  },
  {
    id: '2', sku: 'BAG-002', name: '가죽 토트백', category: '가방',
    price: 289000, image: '👜',
    description: '천연 소가죽으로 제작된 클래식한 디자인의 토트백입니다.',
    rating: 4.5, reviews: 156
  },
  {
    id: '3', sku: 'WATCH-003', name: '스마트워치 프로', category: '전자기기',
    price: 449000, originalPrice: 499000, image: '⌚',
    description: '건강 모니터링과 다양한 스마트 기능을 갖춘 최신 스마트워치.',
    rating: 4.9, reviews: 892
  },
  {
    id: '4', sku: 'SHIRT-004', name: '린넨 셔츠', category: '의류',
    price: 89000, image: '👔',
    description: '시원하고 편안한 착용감의 프리미엄 린넨 셔츠입니다.',
    rating: 4.3, reviews: 78
  },
  {
    id: '5', sku: 'HEADPHONE-005', name: '노이즈캔슬링 헤드폰', category: '전자기기',
    price: 379000, originalPrice: 429000, image: '🎧',
    description: '업계 최고 수준의 노이즈캔슬링 기술이 적용된 무선 헤드폰.',
    rating: 4.7, reviews: 445
  },
  {
    id: '6', sku: 'JACKET-006', name: '방수 자켓', category: '의류',
    price: 249000, image: '🧥',
    description: '가볍지만 완벽한 방수 기능을 갖춘 아웃도어 자켓입니다.',
    rating: 4.6, reviews: 203
  },
]

// Adobe Analytics Tracking Module
const AdobeAnalytics = {
  // Track page view
  trackPageView: (pageName: string, channel: string = 'web') => {
    const data = {
      pageName,
      channel,
      prop1: pageName,
      eVar1: channel,
      events: 'event1' // 페이지뷰 이벤트
    }
    console.log('[AA] Page View:', data)
    return data
  },

  // Track product view (prodView)
  trackProductView: (product: Product) => {
    const data = {
      pageName: `상품상세:${product.name}`,
      products: `;${product.sku}`,
      events: 'prodView',
      prop2: product.category,
      eVar2: product.sku,
      eVar3: product.name,
      eVar4: product.category
    }
    console.log('[AA] Product View:', data)
    return data
  },

  // Track add to cart (scAdd)
  trackAddToCart: (product: Product, quantity: number) => {
    const data = {
      products: `;${product.sku};${quantity};${product.price * quantity}`,
      events: 'scAdd',
      prop3: 'add_to_cart',
      eVar5: product.sku,
      eVar6: quantity.toString()
    }
    console.log('[AA] Add to Cart:', data)
    return data
  },

  // Track remove from cart (scRemove)
  trackRemoveFromCart: (product: Product, quantity: number) => {
    const data = {
      products: `;${product.sku};${quantity};${product.price * quantity}`,
      events: 'scRemove',
      prop3: 'remove_from_cart',
      eVar5: product.sku
    }
    console.log('[AA] Remove from Cart:', data)
    return data
  },

  // Track cart view (scView)
  trackCartView: (cartItems: CartItem[]) => {
    const productString = cartItems
      .map(item => `;${item.sku};${item.quantity};${item.price * item.quantity}`)
      .join(',')
    const data = {
      pageName: '장바구니',
      products: productString,
      events: 'scView',
      prop4: 'cart_view',
      eVar7: cartItems.length.toString()
    }
    console.log('[AA] Cart View:', data)
    return data
  },

  // Track checkout initiation (scCheckout)
  trackCheckoutStart: (cartItems: CartItem[], step: number = 1) => {
    const productString = cartItems
      .map(item => `;${item.sku};${item.quantity};${item.price * item.quantity}`)
      .join(',')
    const totalValue = cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0)
    const data = {
      pageName: `체크아웃:Step${step}`,
      products: productString,
      events: 'scCheckout',
      prop5: `checkout_step_${step}`,
      eVar8: totalValue.toString(),
      eVar9: step.toString()
    }
    console.log('[AA] Checkout Start:', data)
    return data
  },

  // Track purchase (purchase)
  trackPurchase: (cartItems: CartItem[], orderId: string) => {
    const productString = cartItems
      .map(item => `;${item.sku};${item.quantity};${item.price * item.quantity}`)
      .join(',')
    const totalValue = cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0)
    const data = {
      pageName: '구매완료',
      products: productString,
      events: 'purchase',
      purchaseID: orderId, // 중복 방지용 고유 ID
      transactionID: orderId,
      prop6: 'purchase_complete',
      eVar10: orderId,
      eVar11: totalValue.toString(),
      eVar12: cartItems.length.toString()
    }
    console.log('[AA] Purchase:', data)
    return data
  },

  // Track internal search
  trackInternalSearch: (searchTerm: string, resultCount: number) => {
    const data = {
      pageName: '검색결과',
      prop7: searchTerm,
      eVar13: searchTerm,
      eVar14: resultCount.toString(),
      events: 'event2' // 내부 검색 이벤트
    }
    console.log('[AA] Internal Search:', data)
    return data
  },

  // Track promotion click
  trackPromoClick: (promoName: string, promoPosition: string) => {
    const data = {
      prop8: promoName,
      eVar15: promoName,
      eVar16: promoPosition,
      events: 'event3' // 프로모션 클릭 이벤트
    }
    console.log('[AA] Promo Click:', data)
    return data
  }
}

// Main App Component
function App() {
  const [cart, setCart] = useState<CartItem[]>([])
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [isCartOpen, setIsCartOpen] = useState(false)
  const [checkoutStep, setCheckoutStep] = useState(0) // 0: shopping, 1: checkout, 2: complete
  const [orderId, setOrderId] = useState<string>('')
  const [analyticsLog, setAnalyticsLog] = useState<AnalyticsEvent[]>([])

  // Add analytics event to log
  const logAnalyticsEvent = useCallback((eventType: string, details: string, rawData: Record<string, unknown>) => {
    setAnalyticsLog(prev => [{
      timestamp: new Date().toLocaleTimeString('ko-KR'),
      eventType,
      details,
      rawData
    }, ...prev].slice(0, 50))
  }, [])

  // Track initial page view
  useEffect(() => {
    const data = AdobeAnalytics.trackPageView('홈페이지', 'ecommerce')
    logAnalyticsEvent('pageView', '홈페이지 로드', data)
  }, [logAnalyticsEvent])

  // Filter products
  const filteredProducts = products.filter(p => {
    const matchesSearch = p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.category.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === 'all' || p.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  // Get unique categories
  const categories = ['all', ...new Set(products.map(p => p.category))]

  // Handle search
  const handleSearch = (term: string) => {
    setSearchTerm(term)
    if (term.length > 0) {
      const results = products.filter(p =>
        p.name.toLowerCase().includes(term.toLowerCase()) ||
        p.category.toLowerCase().includes(term.toLowerCase())
      )
      const data = AdobeAnalytics.trackInternalSearch(term, results.length)
      logAnalyticsEvent('internalSearch', `검색어: "${term}" (${results.length}건)`, data)
    }
  }

  // Handle product click
  const handleProductClick = (product: Product) => {
    setSelectedProduct(product)
    const data = AdobeAnalytics.trackProductView(product)
    logAnalyticsEvent('prodView', `상품 조회: ${product.name}`, data)
  }

  // Handle add to cart
  const handleAddToCart = (product: Product, quantity: number = 1) => {
    setCart(prev => {
      const existing = prev.find(item => item.id === product.id)
      if (existing) {
        return prev.map(item =>
          item.id === product.id
            ? { ...item, quantity: item.quantity + quantity }
            : item
        )
      }
      return [...prev, { ...product, quantity }]
    })
    const data = AdobeAnalytics.trackAddToCart(product, quantity)
    logAnalyticsEvent('scAdd', `장바구니 추가: ${product.name} x${quantity}`, data)
  }

  // Handle remove from cart
  const handleRemoveFromCart = (productId: string) => {
    const item = cart.find(i => i.id === productId)
    if (item) {
      setCart(prev => prev.filter(i => i.id !== productId))
      const data = AdobeAnalytics.trackRemoveFromCart(item, item.quantity)
      logAnalyticsEvent('scRemove', `장바구니 삭제: ${item.name}`, data)
    }
  }

  // Handle quantity change
  const handleQuantityChange = (productId: string, delta: number) => {
    const item = cart.find(i => i.id === productId)
    if (!item) return

    if (item.quantity + delta <= 0) {
      handleRemoveFromCart(productId)
    } else {
      setCart(prev => prev.map(i =>
        i.id === productId ? { ...i, quantity: i.quantity + delta } : i
      ))
      if (delta > 0) {
        const data = AdobeAnalytics.trackAddToCart(item, delta)
        logAnalyticsEvent('scAdd', `수량 증가: ${item.name} +${delta}`, data)
      } else {
        const data = AdobeAnalytics.trackRemoveFromCart(item, Math.abs(delta))
        logAnalyticsEvent('scRemove', `수량 감소: ${item.name} ${delta}`, data)
      }
    }
  }

  // Handle cart open
  const handleCartOpen = (open: boolean) => {
    setIsCartOpen(open)
    if (open && cart.length > 0) {
      const data = AdobeAnalytics.trackCartView(cart)
      logAnalyticsEvent('scView', `장바구니 조회 (${cart.length}개 상품)`, data)
    }
  }

  // Handle checkout start
  const handleCheckoutStart = () => {
    setCheckoutStep(1)
    setIsCartOpen(false)
    const data = AdobeAnalytics.trackCheckoutStart(cart, 1)
    logAnalyticsEvent('scCheckout', '체크아웃 시작', data)
    const pageData = AdobeAnalytics.trackPageView('체크아웃', 'ecommerce')
    logAnalyticsEvent('pageView', '체크아웃 페이지', pageData)
  }

  // Handle purchase complete
  const handlePurchaseComplete = () => {
    const newOrderId = `ORD-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    setOrderId(newOrderId)
    const data = AdobeAnalytics.trackPurchase(cart, newOrderId)
    logAnalyticsEvent('purchase', `구매 완료: ${newOrderId}`, data)
    setCheckoutStep(2)
    setCart([])
  }

  // Handle promo click
  const handlePromoClick = (promoName: string, position: string) => {
    const data = AdobeAnalytics.trackPromoClick(promoName, position)
    logAnalyticsEvent('promoClick', `프로모션 클릭: ${promoName}`, data)
  }

  // Calculate cart total
  const cartTotal = cart.reduce((sum, item) => sum + item.price * item.quantity, 0)
  const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0)

  // Format price
  const formatPrice = (price: number) => price.toLocaleString('ko-KR') + '원'

  // Render star rating
  const renderStars = (rating: number) => {
    return '★'.repeat(Math.floor(rating)) + '☆'.repeat(5 - Math.floor(rating))
  }

  return (
    <div className="min-h-screen bg-stone-50">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between gap-4">
            <h1
              className="text-xl font-bold text-stone-800 cursor-pointer"
              onClick={() => {
                setCheckoutStep(0)
                const data = AdobeAnalytics.trackPageView('홈페이지', 'ecommerce')
                logAnalyticsEvent('pageView', '홈페이지 이동', data)
              }}
            >
              🛍️ AA Demo Store
            </h1>

            {/* Search */}
            <div className="flex-1 max-w-md">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-stone-400" />
                <Input
                  placeholder="상품 검색..."
                  value={searchTerm}
                  onChange={(e) => handleSearch(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Cart Button */}
            <Sheet open={isCartOpen} onOpenChange={handleCartOpen}>
              <SheetTrigger asChild>
                <Button variant="outline" className="relative">
                  <ShoppingCart className="w-5 h-5" />
                  {cartCount > 0 && (
                    <Badge className="absolute -top-2 -right-2 h-5 w-5 flex items-center justify-center p-0 text-xs">
                      {cartCount}
                    </Badge>
                  )}
                </Button>
              </SheetTrigger>
              <SheetContent className="w-full sm:max-w-md">
                <SheetHeader>
                  <SheetTitle>장바구니 ({cartCount})</SheetTitle>
                </SheetHeader>
                <div className="mt-4 flex flex-col h-[calc(100vh-180px)]">
                  {cart.length === 0 ? (
                    <p className="text-center text-stone-500 py-8">장바구니가 비어있습니다</p>
                  ) : (
                    <>
                      <ScrollArea className="flex-1">
                        <div className="space-y-3 pr-4">
                          {cart.map(item => (
                            <div key={item.id} className="flex gap-3 p-3 bg-stone-50 rounded-lg">
                              <div className="text-3xl">{item.image}</div>
                              <div className="flex-1 min-w-0">
                                <p className="font-medium text-sm truncate">{item.name}</p>
                                <p className="text-stone-600 text-sm">{formatPrice(item.price)}</p>
                                <div className="flex items-center gap-2 mt-2">
                                  <Button
                                    size="icon"
                                    variant="outline"
                                    className="h-7 w-7"
                                    onClick={() => handleQuantityChange(item.id, -1)}
                                  >
                                    <Minus className="w-3 h-3" />
                                  </Button>
                                  <span className="w-8 text-center text-sm">{item.quantity}</span>
                                  <Button
                                    size="icon"
                                    variant="outline"
                                    className="h-7 w-7"
                                    onClick={() => handleQuantityChange(item.id, 1)}
                                  >
                                    <Plus className="w-3 h-3" />
                                  </Button>
                                  <Button
                                    size="icon"
                                    variant="ghost"
                                    className="h-7 w-7 ml-auto text-red-500"
                                    onClick={() => handleRemoveFromCart(item.id)}
                                  >
                                    <Trash2 className="w-4 h-4" />
                                  </Button>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </ScrollArea>
                      <div className="border-t pt-4 mt-4 space-y-3">
                        <div className="flex justify-between text-lg font-bold">
                          <span>총 금액</span>
                          <span className="text-blue-600">{formatPrice(cartTotal)}</span>
                        </div>
                        <Button className="w-full" size="lg" onClick={handleCheckoutStart}>
                          <CreditCard className="w-4 h-4 mr-2" />
                          결제하기
                        </Button>
                      </div>
                    </>
                  )}
                </div>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex gap-6">
          {/* Main Content */}
          <main className="flex-1">
            {checkoutStep === 0 && (
              <>
                {/* Promo Banner */}
                <div
                  className="bg-gradient-to-r from-amber-500 to-orange-500 text-white p-4 rounded-lg mb-6 cursor-pointer hover:opacity-90 transition"
                  onClick={() => handlePromoClick('신년 세일', 'hero_banner')}
                >
                  <div className="flex items-center gap-3">
                    <Tag className="w-6 h-6" />
                    <div>
                      <p className="font-bold text-lg">🎉 신년 특별 세일! 최대 30% 할인</p>
                      <p className="text-sm opacity-90">지금 바로 확인하세요</p>
                    </div>
                  </div>
                </div>

                {/* Category Filter */}
                <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
                  {categories.map(cat => (
                    <Button
                      key={cat}
                      variant={selectedCategory === cat ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => {
                        setSelectedCategory(cat)
                        const data = AdobeAnalytics.trackPageView(cat === 'all' ? '전체상품' : cat, 'ecommerce')
                        logAnalyticsEvent('pageView', `카테고리: ${cat === 'all' ? '전체' : cat}`, data)
                      }}
                    >
                      {cat === 'all' ? '전체' : cat}
                    </Button>
                  ))}
                </div>

                {/* Product Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {filteredProducts.map(product => (
                    <Card key={product.id} className="overflow-hidden hover:shadow-lg transition group">
                      <CardHeader className="p-0">
                        <div
                          className="h-40 bg-stone-100 flex items-center justify-center text-6xl cursor-pointer relative"
                          onClick={() => handleProductClick(product)}
                        >
                          {product.image}
                          <div className="absolute inset-0 bg-black/0 group-hover:bg-black/5 transition flex items-center justify-center">
                            <Eye className="w-8 h-8 text-white opacity-0 group-hover:opacity-70 transition" />
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent className="p-4">
                        <Badge variant="secondary" className="mb-2">{product.category}</Badge>
                        <CardTitle
                          className="text-base mb-1 cursor-pointer hover:text-blue-600"
                          onClick={() => handleProductClick(product)}
                        >
                          {product.name}
                        </CardTitle>
                        <div className="flex items-center gap-1 text-sm text-amber-500 mb-2">
                          <span>{renderStars(product.rating)}</span>
                          <span className="text-stone-400">({product.reviews})</span>
                        </div>
                        <div className="flex items-baseline gap-2">
                          <span className="text-lg font-bold text-blue-600">{formatPrice(product.price)}</span>
                          {product.originalPrice && (
                            <span className="text-sm text-stone-400 line-through">
                              {formatPrice(product.originalPrice)}
                            </span>
                          )}
                        </div>
                      </CardContent>
                      <CardFooter className="p-4 pt-0">
                        <Button
                          className="w-full"
                          onClick={() => handleAddToCart(product)}
                        >
                          <ShoppingCart className="w-4 h-4 mr-2" />
                          장바구니 담기
                        </Button>
                      </CardFooter>
                    </Card>
                  ))}
                </div>

                {filteredProducts.length === 0 && (
                  <div className="text-center py-12 text-stone-500">
                    <p>검색 결과가 없습니다</p>
                  </div>
                )}
              </>
            )}

            {/* Checkout Step 1 */}
            {checkoutStep === 1 && (
              <Card className="max-w-2xl mx-auto">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <CreditCard className="w-5 h-5" />
                    결제 정보 입력
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="bg-stone-50 p-4 rounded-lg space-y-2">
                    <h4 className="font-medium mb-3">주문 상품</h4>
                    {cart.map(item => (
                      <div key={item.id} className="flex justify-between text-sm">
                        <span>{item.image} {item.name} x{item.quantity}</span>
                        <span>{formatPrice(item.price * item.quantity)}</span>
                      </div>
                    ))}
                    <Separator className="my-2" />
                    <div className="flex justify-between font-bold">
                      <span>총 결제금액</span>
                      <span className="text-blue-600">{formatPrice(cartTotal)}</span>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <Label>이름</Label>
                      <Input placeholder="홍길동" />
                    </div>
                    <div>
                      <Label>이메일</Label>
                      <Input type="email" placeholder="example@email.com" />
                    </div>
                    <div>
                      <Label>전화번호</Label>
                      <Input type="tel" placeholder="010-1234-5678" />
                    </div>
                    <div>
                      <Label>배송 주소</Label>
                      <Input placeholder="서울시 강남구..." />
                    </div>
                  </div>
                </CardContent>
                <CardFooter className="flex gap-3">
                  <Button variant="outline" onClick={() => setCheckoutStep(0)}>
                    쇼핑 계속하기
                  </Button>
                  <Button className="flex-1" onClick={handlePurchaseComplete}>
                    결제 완료하기
                  </Button>
                </CardFooter>
              </Card>
            )}

            {/* Checkout Step 2 - Complete */}
            {checkoutStep === 2 && (
              <Card className="max-w-2xl mx-auto text-center">
                <CardContent className="py-12">
                  <CheckCircle2 className="w-16 h-16 text-green-500 mx-auto mb-4" />
                  <h2 className="text-2xl font-bold mb-2">주문이 완료되었습니다!</h2>
                  <p className="text-stone-500 mb-4">주문번호: {orderId}</p>
                  <div className="bg-stone-50 p-4 rounded-lg inline-block">
                    <Package className="w-8 h-8 text-stone-400 mx-auto mb-2" />
                    <p className="text-sm text-stone-600">
                      주문하신 상품은 2-3일 내에 배송될 예정입니다.
                    </p>
                  </div>
                </CardContent>
                <CardFooter className="justify-center">
                  <Button onClick={() => {
                    setCheckoutStep(0)
                    const data = AdobeAnalytics.trackPageView('홈페이지', 'ecommerce')
                    logAnalyticsEvent('pageView', '쇼핑 계속하기', data)
                  }}>
                    쇼핑 계속하기
                  </Button>
                </CardFooter>
              </Card>
            )}
          </main>

          {/* Analytics Log Panel */}
          <aside className="hidden xl:block w-96 shrink-0">
            <Card className="sticky top-20">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  📊 Adobe Analytics 이벤트 로그
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="log">
                  <TabsList className="w-full">
                    <TabsTrigger value="log" className="flex-1 text-xs">이벤트 로그</TabsTrigger>
                    <TabsTrigger value="code" className="flex-1 text-xs">구현 코드</TabsTrigger>
                  </TabsList>
                  <TabsContent value="log">
                    <ScrollArea className="h-[calc(100vh-300px)]">
                      {analyticsLog.length === 0 ? (
                        <p className="text-center text-stone-400 py-8 text-sm">
                          이벤트가 발생하면 여기에 표시됩니다
                        </p>
                      ) : (
                        <div className="space-y-2">
                          {analyticsLog.map((event, idx) => (
                            <div
                              key={idx}
                              className="p-2 bg-stone-50 rounded text-xs border-l-2 border-blue-500"
                            >
                              <div className="flex justify-between items-start mb-1">
                                <Badge variant="outline" className="text-[10px]">
                                  {event.eventType}
                                </Badge>
                                <span className="text-stone-400 text-[10px]">{event.timestamp}</span>
                              </div>
                              <p className="text-stone-700 mb-1">{event.details}</p>
                              <details className="text-stone-500">
                                <summary className="cursor-pointer hover:text-stone-700">데이터 보기</summary>
                                <pre className="mt-1 p-2 bg-stone-100 rounded overflow-x-auto text-[10px]">
                                  {JSON.stringify(event.rawData, null, 2)}
                                </pre>
                              </details>
                            </div>
                          ))}
                        </div>
                      )}
                    </ScrollArea>
                  </TabsContent>
                  <TabsContent value="code">
                    <ScrollArea className="h-[calc(100vh-300px)]">
                      <div className="space-y-3 text-xs">
                        <div className="p-2 bg-stone-900 text-stone-100 rounded font-mono">
                          <p className="text-stone-400 mb-1">// 페이지뷰</p>
                          <code>s.pageName = "홈페이지";</code><br/>
                          <code>s.channel = "ecommerce";</code><br/>
                          <code>s.t();</code>
                        </div>
                        <div className="p-2 bg-stone-900 text-stone-100 rounded font-mono">
                          <p className="text-stone-400 mb-1">// 상품 조회</p>
                          <code>s.products = ";SKU001";</code><br/>
                          <code>s.events = "prodView";</code><br/>
                          <code>s.t();</code>
                        </div>
                        <div className="p-2 bg-stone-900 text-stone-100 rounded font-mono">
                          <p className="text-stone-400 mb-1">// 장바구니 추가</p>
                          <code>s.products = ";SKU001;1;159000";</code><br/>
                          <code>s.events = "scAdd";</code><br/>
                          <code>s.tl(true, 'o', 'Add to Cart');</code>
                        </div>
                        <div className="p-2 bg-stone-900 text-stone-100 rounded font-mono">
                          <p className="text-stone-400 mb-1">// 구매 완료</p>
                          <code>s.products = ";SKU001;1;159000";</code><br/>
                          <code>s.events = "purchase";</code><br/>
                          <code>s.purchaseID = "ORD-123";</code><br/>
                          <code>s.t();</code>
                        </div>
                      </div>
                    </ScrollArea>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </aside>
        </div>
      </div>

      {/* Product Detail Dialog */}
      <Dialog open={!!selectedProduct} onOpenChange={(open) => !open && setSelectedProduct(null)}>
        <DialogContent className="sm:max-w-lg">
          {selectedProduct && (
            <>
              <DialogHeader>
                <DialogTitle>{selectedProduct.name}</DialogTitle>
                <DialogDescription>
                  <Badge variant="secondary">{selectedProduct.category}</Badge>
                  <span className="ml-2 text-amber-500">
                    {renderStars(selectedProduct.rating)} ({selectedProduct.reviews} 리뷰)
                  </span>
                </DialogDescription>
              </DialogHeader>
              <div className="py-4">
                <div className="h-48 bg-stone-100 rounded-lg flex items-center justify-center text-8xl mb-4">
                  {selectedProduct.image}
                </div>
                <p className="text-stone-600 mb-4">{selectedProduct.description}</p>
                <div className="flex items-baseline gap-2 mb-4">
                  <span className="text-2xl font-bold text-blue-600">
                    {formatPrice(selectedProduct.price)}
                  </span>
                  {selectedProduct.originalPrice && (
                    <span className="text-stone-400 line-through">
                      {formatPrice(selectedProduct.originalPrice)}
                    </span>
                  )}
                </div>
                <div className="flex gap-2">
                  <Button
                    className="flex-1"
                    onClick={() => {
                      handleAddToCart(selectedProduct)
                      setSelectedProduct(null)
                    }}
                  >
                    <ShoppingCart className="w-4 h-4 mr-2" />
                    장바구니 담기
                  </Button>
                  <Button
                    variant="secondary"
                    onClick={() => {
                      handleAddToCart(selectedProduct)
                      setSelectedProduct(null)
                      handleCartOpen(true)
                    }}
                  >
                    바로 구매
                  </Button>
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default App
