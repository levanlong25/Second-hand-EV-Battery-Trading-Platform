:: init_all_dbs.bat

echo "=== 1. KHOI TAO USER SERVICE ==="
docker-compose exec user-service flask db init
docker-compose exec user-service flask db migrate -m "Initial user service tables"
docker-compose exec user-service flask db upgrade

echo "=== 2. KHOI TAO LISTING SERVICE ==="
docker-compose exec listing-service flask db init
docker-compose exec listing-service flask db migrate -m "Initial listing service tables"
docker-compose exec listing-service flask db upgrade

echo "=== 3. KHOI TAO AUCTION SERVICE ==="
docker-compose exec auction-service flask db init
docker-compose exec auction-service flask db migrate -m "Initial auction service tables"
docker-compose exec auction-service flask db upgrade

echo "=== 4. KHOI TAO TRANSACTION SERVICE ==="
docker-compose exec transaction-service flask db init
docker-compose exec transaction-service flask db migrate -m "Initial transaction service tables"
docker-compose exec transaction-service flask db upgrade

echo "=== 5. KHOI TAO REVIEW SERVICE ==="
docker-compose exec review-service flask db init
docker-compose exec review-service flask db migrate -m "Initial review service tables"
docker-compose exec review-service flask db upgrade

echo "=== 6. KHOI TAO REPORT SERVICE ==="
docker-compose exec report-service flask db init
docker-compose exec report-service flask db migrate -m "Initial report service tables"
docker-compose exec report-service flask db upgrade

echo "=== 7. KHOI TAO AI PRICING SERVICE ==="
docker-compose exec ai-pricing-service flask db init
docker-compose exec ai-pricing-service flask db migrate -m "Initial ai pricing service tables"
docker-compose exec ai-pricing-service flask db upgrade

echo "=== HOAN TAT! ==="
pause