
sync:
	git submodule foreach git pull
	git submodule foreach git push

pull:
	git submodule foreach git pull

push:
	git submodule foreach git push

setup:
	git submodule init
	git submodule update
	git submodule foreach git checkout master

master:
	git submodule foreach git checkout master

tmpci:
	git submodule foreach git pull
	git submodule foreach git add -A
	git submodule foreach "git commit  -m'tmp ci' || true"
	git submodule foreach git push

update:
	git pull
	git submodule init
	git submodule update
	git submodule foreach git checkout master
	git submodule foreach git pull

test:
	quant-executor start -p ytcj_quotation_crawler crawler.ytcj.kline.m1.daily.stock.debug

#test portfolio

test_circulatestockholder:
	quant-executor start -p public_portfolio_crawler crawler.public.portfolio.circulatestockholder.monthly.debug

test_stockholder:
	quant-executor start -p public_portfolio_crawler crawler.public.portfolio.stockholder.monthly.debug

test_fundstockholder:
	quant-executor start -p public_portfolio_crawler crawler.public.portfolio.fundstockholder.monthly.debug

test_fundownedlist:
	quant-executor start -p public_portfolio_crawler crawler.public.portfolio.fundownedlist.monthly.debug

#test consult

test_nbjy:
	quant-executor start -p public_portfolio_crawler crawler.public.portfolio.consult.nbjy.monthly.debug

test_dzjy:
	quant-executor start -p public_portfolio_crawler crawler.public.portfolio.consult.dzjy.monthly.debug

test_xsjj:
	quant-executor start -p public_portfolio_crawler crawler.public.portfolio.consult.xsjj.monthly.debug

test_lsfh:
	quant-executor start -p public_portfolio_crawler crawler.public.portfolio.consult.lsfh.monthly.debug

# test simu
test_simu_mainhold:
	quant-executor start -p public_portfolio_crawler crawler.public.portfolio.simu.mainhold.monthly.debug

test_simu_advisor:
	quant-executor start -p public_portfolio_crawler crawler.public.portfolio.simu.advisor.monthly.debug

test_simu_im:
	quant-executor start -p public_portfolio_crawler crawler.public.portfolio.simu.im.monthly.debug

test_simu_pep:
	quant-executor start -p public_portfolio_crawler crawler.public.portfolio.simu.pep.monthly.debug

test_symbol_list_us:
	quant-executor start -p public_portfolio_crawler crawler.public.portfolio.symbollistus.monthly.debug

test_insider_transaction_us:
	quant-executor start -p public_portfolio_crawler crawler.public.portfolio.insidertransactionus.monthly.debug

test_top_institutional_holders_us:
	quant-executor start -p public_portfolio_crawler crawler.public.portfolio.topinstitutionalholdersus.monthly.debug

test_top_mutual_fund_holders_us:
	quant-executor start -p public_portfolio_crawler crawler.public.portfolio.topmutualfundholdersus.monthly.debug

test_hedge_funds_list_us:
	quant-executor start -p public_portfolio_crawler crawler.public.portfolio.hedgefundslistus.monthly.debug

test_hedge_fund_us:
	quant-executor start -p public_portfolio_crawler crawler.public.portfolio.hedgefundus.monthly.debug

test_hedge_fund_us_whale:
	quant-executor start -p public_portfolio_crawler crawler.public.portfolio.hedgefunduswhale.monthly.debug

test_stock_price_us:
	quant-executor start -p public_portfolio_crawler crawler.public.portfolio.stockpriceus.monthly.debug

test_stock_tree_apple:
	quant-executor start -p public_portfolio_crawler crawler.public.portfolio.stocktreeapple.monthly.debug

test_rights_changes_hk:
	quant-executor start -p public_portfolio_crawler crawler.public.portfolio.rightschangeshk.monthly.debug

test_fund_list:
	quant-executor start -p public_portfolio_crawler crawler.public.portfolio.fund.fundlist.monthly.debug

test_calendar_en:
	quant-executor start -p public_portfolio_crawler crawler.public.portfolio.calendar_en.monthly.debug
