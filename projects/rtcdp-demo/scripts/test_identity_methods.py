"""
Identity Descriptor 기능 테스트 스크립트
새로 추가된 메서드들이 올바르게 정의되었는지 확인
"""

import sys
import inspect
from pathlib import Path

# aep_schema_builder 모듈 임포트
sys.path.insert(0, str(Path(__file__).parent))

try:
    from aep_schema_builder import AEPSchemaBuilder
    print("✓ AEPSchemaBuilder 모듈 임포트 성공\n")
except ImportError as e:
    print(f"❌ 모듈 임포트 실패: {e}")
    sys.exit(1)

# 새로 추가된 메서드 목록
REQUIRED_METHODS = [
    'create_identity_namespace',
    '_get_identity_namespace',
    'create_identity_descriptor',
    'setup_lookup_identity'
]

print("=== Identity 관련 메서드 검증 ===\n")

# 클래스 메서드 확인
for method_name in REQUIRED_METHODS:
    if hasattr(AEPSchemaBuilder, method_name):
        method = getattr(AEPSchemaBuilder, method_name)
        sig = inspect.signature(method)

        print(f"✓ {method_name}")
        print(f"  Signature: {sig}")

        # Docstring 확인
        if method.__doc__:
            doc_first_line = method.__doc__.strip().split('\n')[0]
            print(f"  Doc: {doc_first_line}")

        print()
    else:
        print(f"❌ {method_name} - 메서드가 존재하지 않습니다\n")

# 초기화 시 identity_api 속성 확인
print("\n=== 초기화 검증 ===\n")

try:
    # 환경 변수 없이 초기화 시도하면 에러 발생
    # 여기서는 클래스 정의만 확인
    init_signature = inspect.signature(AEPSchemaBuilder.__init__)
    print(f"✓ __init__ signature: {init_signature}")

    # __init__ 소스 코드에서 identity_api 설정 확인
    init_source = inspect.getsource(AEPSchemaBuilder.__init__)

    if 'self.identity_api' in init_source:
        print("✓ self.identity_api 속성 설정 확인됨")

        # 실제 URL 추출
        for line in init_source.split('\n'):
            if 'self.identity_api' in line and '=' in line:
                print(f"  {line.strip()}")
    else:
        print("❌ self.identity_api 속성이 설정되지 않음")

except Exception as e:
    print(f"⚠ 초기화 검증 중 에러: {e}")

print("\n=== create_schema() 메서드 Lookup Identity 통합 확인 ===\n")

try:
    create_schema_source = inspect.getsource(AEPSchemaBuilder.create_schema)

    # Lookup 감지 로직 확인
    if 'lookup' in create_schema_source.lower():
        print("✓ 'lookup' 키워드 감지 로직 존재")

    if 'setup_lookup_identity' in create_schema_source:
        print("✓ setup_lookup_identity() 호출 확인됨")

        # 관련 코드 라인 추출
        for i, line in enumerate(create_schema_source.split('\n')):
            if 'setup_lookup_identity' in line:
                print(f"  Line {i}: {line.strip()}")
    else:
        print("❌ setup_lookup_identity() 호출이 create_schema()에 통합되지 않음")

except Exception as e:
    print(f"⚠ create_schema() 검증 중 에러: {e}")

print("\n" + "="*60)
print("검증 완료!")
print("="*60)
print("\n실제 API 호출 테스트는 AEP 환경 변수 설정 후:")
print("  python aep_schema_builder.py --create ../schemas/product-lookup-schema.json")
