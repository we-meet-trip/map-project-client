# 행정경계 데이터 라이선스

이 폴더의 `provinces.geojson`·`districts.geojson` 은 OpenStreetMap 자료로 만든 파생 데이터베이스다.

- 출처: © OpenStreetMap contributors — <https://www.openstreetmap.org/copyright>
- 해안선(바다 쪽을 덜어 낸 육지 다각형): OpenStreetMap Data(osmdata.openstreetmap.de), © OpenStreetMap contributors
- 라이선스: Open Data Commons Open Database License(ODbL) 1.0 — <https://opendatacommons.org/licenses/odbl/1-0/>
- 만드는 방법: `python3 scripts/build_geo.py`(받은 경계를 앱 지역 목록에 맞춰 고르고 육지로 자른 뒤 단순화한다)

이 두 파일은 저장소의 MIT 라이선스가 아니라 ODbL 을 따른다. 고치거나 이 파일로 새 데이터베이스를 만들어
배포하면 그 결과도 ODbL 로 배포해야 하고, 위 출처를 함께 표시해야 한다. 앱은 지도 화면에
"© OpenStreetMap contributors" 를 표시한다.
