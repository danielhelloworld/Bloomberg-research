from pathlib import Path
import json, html, csv, re, zipfile

P=Path(__file__).resolve().parent
R=json.loads((P/'risk_comparison.json').read_text(encoding='utf-8'))
lanes=[json.loads((P/f).read_text(encoding='utf-8')) for f in ['lane_health_consumer.json','lane_growth_industrial.json','lane_energy_finance_japan.json']]
raw={s['ticker']:s for d in lanes for s in d['stocks']}
quotes=json.loads(json.loads((P/'quotes.json').read_text(encoding='utf-8'))['content'][0]['text'])
quotes={q['symbol'].replace('.US',''):q for q in quotes}
CONS=json.loads((P/'consensus_summary.json').read_text(encoding='utf-8'))
OLD=R['models']['原B_75']; NEW=R['models']['修订B_50']; START=R['models']['修订B周一20']
ORDER=[s for s in NEW if s!='CASH']
E=lambda x:html.escape(str(x),quote=True)
notes={}
def add(t,name,role,case,facts,quality,valuation,event,bear,kill,decision,proof):
    notes[t]=dict(name=name,role=role,case=case,facts=facts,quality=quality,valuation=valuation,event=event,bear=bear,kill=kill,decision=decision,proof=proof)

add('XOM','埃克森美孚','能源敞口；油企合计按同一风险管理',
'一体化上游、炼化和化工业务，使公司既受原油影响，也受成品油价差与装置开工率影响。低成本供给和现金回报是持有依据；油价上涨本身不能证明股票仍有超额收益。',
['2026Q2 GAAP 净利润145.25亿美元，调整后146.80亿美元；差额虽小，实际包含 identified items -26.38亿美元与 timing effects +24.83亿美元的相互抵销。','Q2经营现金流235.55亿美元，公司口径FCF 172.36亿美元；H1经营现金流322.60亿美元、营运资本消耗39亿美元。6月底债务约424亿美元、现金约106亿美元。','10/16已发布Q3因素桥：炼油产品利润率约+45亿美元、液体价格约-13亿美元、预期时点效应约-25亿美元。公司明确该桥不是完整盈利预测。'],
'现金创造与资本结构支持持有，但商品周期、库存与交易确认时点会造成季度波动。公司FCF包含资产出售等定义项目，不与其他公司的“CFO减资本开支”机械横比，也不把单季高利润乘四。',
'10/22收盘178.23美元；本轮盘中参考183.00美元。缺少经核实的中周期油价、炼油利润率和完整前瞻盈利模型，因此不声称已证明低估。应在不同商品价格下核对资本开支、股息覆盖与估值。',
'10/30美股盘前财报：公司日历为05:30 CT发布、08:30 CT电话会，对应北京时间18:30与21:30。已知炼油利好需要实际现金流验证。',
'需求衰退与供给恢复可同时压低原油和炼油价差；战争升级也可能导致装置中断、特别税或经营损失。能源股票不能被当作组合的确定性对冲。',
'若实际现金转化明显弱于10/16因素桥能解释的范围、剔除营运资本及出售资产后无法覆盖既定资本开支与股息，停止扩仓并重估。',
'旧目标8%降至5%；周一仅2%。与CVX合计：财报前3%、验证后上限8%。',
'财报的产量、价差、现金流桥相互吻合，现金分配未依靠持续加杠杆，且重新报价后估值仍可接受。')

add('CVX','雪佛龙','与XOM共享商品价格和同日财报风险',
'上游产量增长与Tengiz等项目现金回收可以支持回报，但Hess并表造成的规模增长需要与内生增长拆开。持有理由是现金创造和资产质量，不是再买一只油股就完成分散。',
['Q2 GAAP净利润120.72亿美元、调整后119.77亿美元，EPS分别6.11与6.06美元。资产处置、养老金和外汇项目需逐项看。','Q2经营现金流226亿美元，剔除营运资本后约197亿美元；公司FCF约181亿美元，含约14亿美元时点影响。H1 CFO 251.47亿美元减资本开支86.01亿美元为165.46亿美元。','Q2产量约407万桶油当量/日、同比+20%，包含Hess并表影响。债务含融资租赁约371亿美元，现金约85亿美元。'],
'营运资本释放使当季现金显得强，不能将其视为每季重复收益。TCO分配、资产出售和并购带来的现金/产量变化，应与持续经营分开核对。',
'10/22收盘226.68美元、盘中参考233.18美元。周期顶端的低P/E可能是陷阱；本轮没有足够证据给出可审计的中周期合理价或目标价。',
'10/30 Q3披露/电话会，与XOM同日；公司日历确认电话会11:00 ET，确切新闻稿发布时间执行前再核对。重点看营运资本、TCO分配、Hess整合与资本开支。',
'油价与炼油利润同时下降、项目兑现不足或并购整合抬高成本，会同时损害现金与估值。不能假定XOM涨、CVX跌就能自然对冲。',
'若剔除时点及营运资本后股息与资本开支覆盖恶化，或产量增长主要来自并表而现金回报不及投入，冻结加仓。',
'旧4%降至3%；周一1%。权重受能源合并预算约束。',
'经营现金流的改善在剔除一次性因素后仍存在，项目现金回收与负债趋势一致。')

add('JNJ','强生','医疗防守核心，但有法律与并购风险',
'创新药和医疗器械提供多条收入来源，需求较稳定。投资问题是这些业务带来的现金是否足以覆盖诉讼、并购和当前较高估值，而非只看“医疗防守”标签。',
['Q3销售253.99亿美元、同比+5.9%；GAAP EPS仅0.09美元，调整后2.59美元、同比-7.5%。FY26调整后EPS指引11.05—11.15美元。','管理层称Q3 FCF超过60亿美元、全年约210亿美元；该数字属于公司估计，本轮尚未完成Q3全部现金流表勾稽。净债务约280亿美元。','拟议卵巢癌滑石粉和解55亿美元，取决于95%剩余索赔人参与等条件；Firefly/Sail交易预计令2027调整后EPS稀释约1.36美元。'],
'GAAP与调整后利润差异大，诉讼即使被调整后利润剔除仍有经济成本。并购还会影响下一年的盈利基准，不宜把FY26的调整后EPS视为永久盈利。',
'盘中263.37美元除以FY26指引中值11.10美元，约23.73倍、调整后盈利收益率4.21%。低增长环境下该估值并不自动便宜；这也不是GAAP P/E。',
'Q3已经公布。12/8企业战略回顾在比赛11/13结束之后，不能算短期获利催化。近期诉讼与管线消息仍有不定时风险。',
'防守交易拥挤导致估值收缩，同时和解条件未满足、器械执行偏弱或并购稀释超预期。经营稳定不能保证股价稳定。',
'若全年调整后EPS下沿低于11.05美元、FCF指引低于约210亿美元，或和解负担显著扩大，重新审查。',
'旧8%降至5%；周一3%。保留现金流防守作用，降低单名法律事件敞口。',
'法律条件、现金流与器械业务执行继续支持全年指引；不能只因板块强势而加到原8%。')

add('ABBV','艾伯维','盈利型医疗，集中于Skyrizi/Rinvoq',
'免疫产品的高增长支持公司度过旧产品衰退，但新产品集中度、研发收购和股息支付共同约束自由现金。比JNJ更偏向产品兑现和财报事件。',
['Q2收入169.90亿美元、同比+10.2%；调整后EPS3.65美元、GAAP2.03美元。Skyrizi 55.05亿美元加Rinvoq 25.25亿美元，占收入约47.3%。','H1 CFO72.65亿美元减资本开支5.87亿美元，FCF66.78亿美元；同期股息61.56亿美元，扣股息仅剩5.22亿美元，尚未扣回购、并购与还债。','10/5最新8-K计入约2.16亿美元IPR&D费用、每股约0.11美元影响；Q3调整后指引更新为3.73—3.77美元、全年13.76—13.96美元，替代7月旧指引。'],
'盈利增长真实存在，但调整后利润会剔除研发收购成本，而这些成本与经营战略有关。6月底债务约708.22亿美元、现金65.69亿美元，之后交易还可能改变杠杆。',
'盘中285.36美元除以更新后的全年中值13.86美元约20.59倍。供应商Q3 normalized EPS 3.7788与公司更新指引上沿接近但略高，定义和修订时点未对齐前不能当作确定预期差。',
'10/30盘前财报。10/22 lutikizumab试验利好对应的申报预计2027下半年，不能直接计作比赛期间销售或现金收入。',
'两大产品增长放缓、药价政策压价、并购开支及债务负担叠加，造成调整后EPS好看而可分配现金不足。',
'若收入增长无法转化为剔除营运资本后的现金、股息和杠杆压力上升，或新指引再次下调，取消扩仓。',
'旧4%降至3%；周一0%，等财报。',
'用10/5之后的同口径盈利基准核查结果，并确认核心产品增长、现金覆盖与资本分配。')

add('PG','宝洁','已披露业绩的消费现金流核心',
'品牌、渠道与日常消费需求支撑现金流。需要证明增长来自销量与产品组合，而不是只依赖提价，同时防范低增长公司估值过高。',
['FY27Q1销售232.76亿美元；有机增长4%、销量增长2.4%；核心EPS2.00美元、同比+1%，GAAP EPS1.97美元。核心利润率同比约下降80基点。','FY27核心EPS指引6.89—7.11美元；有机增长指引1%—3%。本季度较好增长不等于全年会同步上调。','FY27Q1 CFO57.67亿美元减资本开支13.66亿美元，FCF44.01亿美元。9月底现金153.65亿美元，短债170.28亿美元、长债218.97亿美元，为10/1交易前时点。'],
'现金转化较好，但利润率下滑说明成本与营销投入仍在侵蚀增量收入。不能把交易前现金余额当作当前可用现金；旧授信到期后的安排需另核实。',
'盘中161.12美元除以全年核心EPS中值7.00美元，约23.02倍。估值需要与1%—3%的有机增长和核心利润率一起判断，并非无条件避险资产。',
'本季已公布，下一季度业绩不在近期主要财报集群内。短期股价更依赖消费防守轮动与估值变化。',
'销量转弱、利润率继续下降、美元升值或防守拥挤交易逆转，均可能导致盈利和估值同时受压。',
'有机销量转负且核心利润率继续恶化，或全年核心EPS下沿下调，暂停增加；价格上涨不能替代基本面证据。',
'保留7%条件目标；周一3%，不因短期上涨一次到位。',
'销量、利润率和FCF至少保持当前经营逻辑；以新价格重新评估盈利收益率。')

add('WMT','沃尔玛','零售防守，但估值容错较低',
'规模、低价和全渠道履约构成优势，广告与电商能改善收入质量。投资判断的关键是这些改善能否持续，而不是将食品零售与低股价波动划等号。',
['FY27Q2收入约1879亿美元、同比+5.9%；电商+23%、广告+38%、美国同店+2.6%。全年调整后EPS指引2.80—2.87美元。','H1 CFO197.10亿美元减资本开支141.81亿美元，FCF55.29亿美元，低于上年同期69.43亿美元、约下降20.4%。','Q2有约29亿美元关税退款，基本已收到。退款带来的利润或现金改善不能被重复外推到以后季度。'],
'经营模式有韧性，但高资本投入和一次性退款使“利润增长”与“持续FCF增长”并不等价。要看剔除退款后利润率和电商单位经济性。',
'盘中119.87美元除以全年指引中值2.835美元，约42.28倍。若盈利不变、仅倍数降至36或32倍，价格敏感性约-14.9%或-24.3%；这是估值情景，不是目标价。',
'下一次财报11/19，在11/13比赛结束之后。短期组合不能靠这次财报兑现估值。',
'高估值遇到防守轮动退潮，同时退款不重复、消费者承压或资本开支超计划。',
'剔除退款后的增长与利润率不足以支撑高倍数，或FCF持续落后而估值仍上升时，压低仓位。',
'旧5%降至3%；周一2%。不把其当作PG的完全替代，也不为了防守标签维持高仓位。',
'确认非一次性经营改善，并在重新报价后仍有合理回报空间。')

add('JPM','摩根大通','盈利与资本较强的银行；承受信用尾部风险',
'规模、存款基础与多元化业务提供收入来源，但银行本质仍是有杠杆的信用与期限转换。净息差、费用、资本回报与信用损失必须一起看。',
['Q3净利润153.05亿美元、EPS5.57美元；剔除投资证券税前损失6.58亿美元后约158亿美元、EPS5.75美元。ROTCE约20%，调整后约21%。','管理口径收入509.07亿美元、同比+8%；费用272.95亿美元、同比+12%。信用成本27.43亿美元，包含约22亿美元净核销与5.39亿美元净准备金增加，后者不是拨备释放。','每股有形净资产112.64美元，标准法CET1约13.9%；管理层降低回购力度。2026 NII ex-Markets约972亿美元，2027初步约1070亿美元，并非无条件兑现。'],
'费用增速快于收入、净拨备增加，意味着盈利强不能消除信用周期风险。银行CFO、企业净债务与工业企业FCF指标不宜直接比较。',
'10/22收盘336.54美元相当于约2.99倍有形账面价值。高ROTCE支持溢价，但如果信用成本和资本要求上升，倍数也会回落；不以低TTM P/E认定便宜。',
'Q3已披露。比赛内主要看利率曲线、信用环境、回购与管理层展望变化，无需承受下周银行财报集群。',
'衰退、失业和信用卡/商业贷款损失上升，同时费用与监管资本约束减少股东回报。',
'若信用恶化超过管理层原解释、费用失控或CET1/回购策略明显转弱，重估；不能因为跌破买入价就自动摊低。',
'保留6%条件目标；周一4%。这是首批中较大的信用敞口，必须与BRK及现有防守资产合并看。',
'信用成本、存款成本与资本充足度支持盈利持续性。以-30%严重单名情景检验时，6%仓位仍可损失1.8%净值。')

add('BRK.B','伯克希尔B','保险与实业组合；有现金但不等于现金',
'保险浮存金、铁路、公用事业和制造服务业务提供多元收入来源。集团现金多给资本配置带来选择权，但现金、保险负债及受监管子公司资产不能无条件互相抵销。',
['Q2净利润256.67亿美元，含投资收益126.84亿美元；经营利润129.83亿美元、同比+16.34%。','经营利润包含外汇收益3.26亿美元，而上年同期外汇损失8.77亿美元。仅剔除该债务外汇影响，经营利润增速约5.15%，仍非完全正常化口径。','保险承保利润17.31亿美元、低于19.92亿美元；GEICO综合成本率91.2%，上年83.5%。H1 CFO216.53亿美元减资本投入106.31亿美元，差额110.22亿美元，不等于所有者收益。'],
'股市投资收益与外汇会放大GAAP利润。保险与其他部门现金及国库券约3600亿美元，与集团总现金口径不同；铁路/公用事业债务不能简单用集团现金净额抹去。',
'按官方权益及A/B股换算，B股每股账面价值约348.26美元；10/22收盘546.97美元，约1.57倍账面。P/B是观察点，不能单独构成公允价值结论。',
'下一次Q3披露可能在11月初，但本轮没有核实具体官方日期；不能把某个周六日期写成确定事件。',
'巨灾损失、保险费率/承保恶化、股市下跌与实业衰退可能相关；现金多也可能在短赛程里拖累相对表现。',
'GEICO承保持续恶化、巨灾准备不足、资本配置纪律变化或实业现金流转弱，削弱防守逻辑。',
'保留6%条件目标；周一3%。不把BRK计入无风险现金。',
'承保质量与实业经营现金足够稳定，并确认资本配置没有新增不可理解风险。')

add('MSFT','微软','AI平台中优先保留，但等待财报证明现金回报',
'Azure、企业软件和分发渠道带来黏性与定价权。核心矛盾是AI需求增长能否转化为可分配现金，而不是只看订单、收入或调整后EPS。',
['FY26Q4 CFO554.41亿美元减现金购建PPE358.02亿美元，现金FCF196.39亿美元；上年同期255.68亿美元。全年CFO1829.35亿美元减PPE1159.48亿美元，FCF669.87亿美元。','Q4披露资本开支410亿美元，含融资租赁约56亿美元。商业RPO 6780亿美元、同比+84%，但剔除OpenAI后增长25%。调整后EPS仍含部分离散收益，不等于剔除全部一次性。','FY27Q1收入指引898.5—909.5亿美元、Azure固定汇率增长约45%、资本开支超过500亿美元。建筑/数据中心使用年限从15年延至25年会改变租赁分类，可比性需重建。'],
'现金证据强于单看投资收益的利润指标，但新增经营现金被资本开支吸收。融资租赁本金应单独看；已经进入CFO的租赁费用不能再全部重复扣除。6月底未起租承诺3291亿美元也不等于全部已入账金融债务。',
'以10/22收盘521.08美元及供应商股本估算，FY26现金FCF收益率约1.73%；再减全年融资租赁本金31.01亿美元的分析敏感性约1.65%。不是前瞻收益率或目标价，低收益率意味着现金回报需要继续增长。',
'10/28盘后财报。重点看Azure相对公司约45%指引、下一季展望、剔除模型客户集中度后的RPO，以及现金资本开支与新增租赁。',
'需求利用率不及投入、GPU更新快、租赁支付增加，同时市场下调长期增长与估值。账面资本开支因分类下降并不代表经济负担下降。',
'Azure同时弱于原指引且下一季继续降速，或现金/利润率恶化来自利用率不足而非暂时交付节奏，取消加仓。',
'保留5%条件目标；周一0%。科技预算优先留给现金质量相对清楚的公司。',
'财报后重做现金流桥，确认增长、下一季指引与资本回报一致，再分两次考虑2%和3%；不是按日期自动买入。')

add('GOOGL','Alphabet','搜索与云业务有增长，但GAAP估值被投资收益扭曲',
'搜索分发和广告效果、Cloud与模型生态提供商业化入口。要区分经营增长、并购贡献和投资资产重估，并承担AI替代传统搜索及监管风险。',
['Q2收入1197.96亿美元、同比+24%；经营利润407.70亿美元。Cloud收入247.68亿美元、同比+82%，经营利润88.14亿美元；搜索收入632.71亿美元、同比+17%。','GAAP EPS9.11美元，其他收益979.83亿美元，主要受约990.31亿美元股权投资收益影响；这不是搜索广告在一个季度创造的经营利润。','Q2 CFO约391亿美元、资本开支约449亿美元，现金差额约-58亿美元；H1 CFO848.59亿美元减资本开支805.98亿美元，仅余42.61亿美元。H1折旧约135.86亿美元，上年94.85亿美元。'],
'经营端增长较强，但Wiz并表使Cloud增长不能全视为内生，公允价值变动又使GAAP利润与现金脱节。融资增加、未来租赁承诺也需和AI投入一起看。',
'供应商TTM P/E约16倍会被投资收益拉低，不能据此说比其他平台便宜。本轮未取得可核实的全年正常化EPS与NTM一致预期，不用单季EPS乘四替代。',
'10/28盘后财报/电话会：日期来自公司公告的分发文本，本轮IR主站未单独显示该条完整公告，执行前再核对。搜索变现、Cloud内生增长及利润率、现金资本开支、折旧和下一季指引，比GAAP EPS headline重要。',
'AI搜索改变流量与单位成本、反垄断限制分发、云资本开支尚未变现，同时投资资产价格回撤。',
'广告增长与云现金创造无法覆盖更高折旧和资本支出，或把持续投资收益当作估值支柱，暂停扩仓。',
'旧5%降至3%；周一0%。与MSFT、AMZN、ETN共享AI支出周期，不能视作四项独立风险。',
'剔除股权重估后，搜索和Cloud经营证据仍支持估值；财报后再更新现金与盈利基准。')

add('AMZN','亚马逊','业务增长强，但现金投入与投资收益使短期仓位更难定价',
'电商规模、Prime、广告及AWS构成多条增长引擎。问题是云与AI收入增长是否足以覆盖基础设施投入和融资负担，尤其在比赛的短窗口内。',
['Q2收入2006.06亿美元、同比+20%；经营利润274.61亿美元。AWS收入约422亿美元、同比+37%，经营利润约166亿美元。','GAAP EPS5.75美元含约534亿美元Anthropic税前投资收益。过去十二个月CFO1614.03亿美元减PPE1690.07亿美元，现金FCF为-76.04亿美元。','H1债务融资流入669.98亿美元；金融债务1322.24亿美元，高于年末683.96亿美元。租赁现值1097.71亿美元、未起租承诺1372.14亿美元，另有未支付PPE206.20亿美元。'],
'盈利与AWS增长不能消除现金投入压力。融资并非自动利空，但必须确认新投入在产生足够经济回报；供应商低TTM P/E受投资收益影响。',
'不以当前约20倍GAAP TTM P/E认定低估。公司Q3收入指引1970—2020亿美元、经营利润225—265亿美元；供应商收入一致预期约2022.03亿美元，已略高于公司收入指引上沿。',
'10/29盘后财报。重点看AWS增速和利润率、经营利润相对公司指引，以及租赁/现金资本开支、供应商付款和负债变化。',
'增长兑现而股价仍下跌的可能机制是：市场已要求指引上沿，资本投入继续吞噬现金，同时投资收益回落。',
'资本支出与融资继续上升、现金转化恶化，或经营利润低于指引而无法解释，不加仓；不能靠“AI长期空间”解释所有短期损失。',
'旧3%降至0%，保留观察。这里是取消候选建仓，不是要求卖出尚不存在的AMZN持仓。',
'若财报证明经营利润、现金和资本效率改善，可提议用最多2%替换其他AI预算；不得在现有AI预算上直接叠加。')

add('LMT','洛克希德马丁','国防订单与现金流，但合约资产和追涨风险需约束',
'政府长周期项目和导弹补库支持订单可见性；真正归属于股东的是履约利润与现金，而不是订单名义总额。固定价格合同与预算拨付构成主要执行风险。',
['Q3收入207.11亿美元、同比+11%，EPS7.97美元；经营现金流约34亿美元、FCF约30亿美元，低于上年约37与33亿美元。订单积压约2920亿美元，含PAC-3约525亿美元大额订单。','FY26 EPS指引30.35—30.75美元、FCF78—80亿美元。前9个月CFO68.93亿美元减资本开支12.68亿美元，FCF56.25亿美元。','合约资产168.99亿美元，高于年末130.01亿美元；F-35 Lot20存在成本超过授权等现金风险。F-16与C-130各有约0.4亿美元利润调减；拟议Ultra Maritime收购约34.5亿美元。'],
'订单增长与现金改善不同步，合约资产占用可能延迟现金回收。不能把每个国防合同当作立刻确认的利润，也要给并购支付和项目损失留余量。',
'10/22收盘589.91美元除以EPS中值30.55美元约19.31倍；按公司全年FCF中值估算股权FCF收益率约5.8%，依赖指引兑现。本轮盘中价格已更高，买入前必须重算。',
'10/22财报已经公布。近期约10个交易日涨幅16.15%，公开订单利好可能已有相当部分被交易，不能默认未计价。',
'停火预期导致主题回吐，或项目执行、现金授权、拨付和并购支出同时恶化。即使国防需求长期高，股票短期也会回撤。',
'FCF指引下降、合约资产持续上升而收款解释不足，或新项目损失扩大，停止加仓；回调后也需重新核查。',
'保留4%条件目标；周一2%，分批防止追逐财报后的价格跳升。',
'价格提供可接受现金收益率，订单到收款的路径未恶化，才考虑增加剩余2%。')

add('ETN','伊顿','AI电力基础设施，但与云平台共享投资周期',
'配电、电气设备与数据中心建设需求支持订单。与平台公司的业务模式不同，但同样依赖AI资本支出持续兑现，不能用不同产业分类掩盖共同终端需求。',
['Q2收入85.31亿美元、同比+21%，内生增长14%；分部利润率23.1%、下降约80基点。Electrical Americas订单+41%、Global+33%，book-to-bill约1.2。','Q3公司指引内生增长13.5%—15.5%，利润率24.6%—25.0%，GAAP EPS2.77—2.87、调整后3.46—3.56美元。全年调整后EPS13.40—13.60，GAAP10.36—10.56美元。','Q2 CFO11.27亿美元减资本开支2.53亿美元，FCF8.74亿美元。债务约206.11亿美元，上年底98.95亿美元；Boyd收购约95.5亿美元，并表抬高表面增长。'],
'订单强并不等于当前现金回报强。摊销、交易和重组调整使调整后EPS高于GAAP；需要证明并购整合与有机利润率能支撑估值。',
'10/22收盘368.99美元除以全年调整后EPS中值13.50美元约27.33倍；除以GAAP中值约35.28倍。两种口径都需展示，不能只选择较低倍数。',
'11/3盘前财报，处于比赛窗口。供应商Q3 normalized EPS3.5463已接近公司指引上沿3.56美元，订单强未必足以形成预期差。',
'AI建设放缓、客户延后订单、订单转收入不及预期，叠加并购杠杆与利润率压力，估值与盈利同时下修。',
'内生订单或利润率不及公司指引，或现金改善落后于并购后利润，取消引入。',
'旧3%降至0%。观察仓也占风险预算，不为“完整产业链”强行配置。',
'11/3后若订单、内生利润率与现金兑现，可用至多2%—3%替换AI组其他仓位；需重新计算组内暴露。')

add('TM','丰田','制造业与日元双重敞口；交易资格需单独验证',
'全球制造与混动产品结构提供规模优势，但汽车周期、关税、汇率与金融子公司的融资风险相互交织。美元计价ADR并不消除日本盈利与日元的影响。',
['FY27Q1收入13.5254万亿日元、同比+10.4%，营业利润1.0634万亿日元、同比-8.8%；净利润1.477万亿日元、同比+75.6%，营业与净利方向不同。','其他金融收益0.8506万亿日元，上年0.1537万亿；汇兑收益约0.1124万亿，上年汇兑损失0.2124万亿。不能把净利增长全当作汽车销售盈利增长。','经营现金流0.5365万亿日元，上年1.8765万亿；营运资产消耗与税款有影响。全年营业利润指引3.0升至3.4万亿日元，但USD/JPY假设由150改为160。'],
'更弱日元有助日元报表利润，却可能损害美元ADR换算，两个作用可抵销。金融子公司债务有应收资产支持，不应直接把集团净债务当作工业业务杠杆。',
'10/22 ADR收盘198.22美元。供应商美元EPS与公司日元EPS的ADR比例、汇率及期间未完成勾稽，约8倍TTM P/E不能作为建仓依据。',
'下一次财报在11月初附近，但本轮未完成官方具体日期核实。TM是ADR，是否符合本账户“正股”及WLS范围需在终端验证。',
'关税与北美需求恶化、日元反弹压低营业利润、金融业务信用损失上升，以及ADR汇率换算。',
'若升指引主要依赖汇率而汽车利润率和现金继续恶化，维持不配置；无法确认合规交易资格时权重为0。',
'旧4%降至0%。取消为地域分散而被动占位的仓位。',
'只有交易资格、财报日期、工业现金流和汇率/ADR盈利桥全部清楚后，才考虑用最多2%替换其他周期股。')

add('NEE','新纪元能源','受监管电力加能源开发；长久期融资敏感',
'电力需求增长和受监管资产回报提供长期增长基础，但资本密集、利率、融资与并购决定股东能否获得这些回报。它不是短期无风险公用事业替代品。',
['Q3 GAAP EPS2.28美元，调整后1.24美元；非合格套期项目税后约影响1.07美元/股。全年调整后EPS指引3.92—4.02美元，管理层指向高端。','前9个月CFO123.22亿美元，相比增长及核电投资275.54亿美元有152.32亿美元资金缺口；这是投资融资敏感性，不是公司定义FCF。同期融资流入175.22亿美元、新债182.32亿美元。','Q3衍生品账面收益约30.45亿美元，其中未实现约30.05亿美元。公司FFO/debt目标与评级阈值接近，目标不是已经实现的当期值。'],
'GAAP盈利受套期重估放大，资本开支与外部融资是关键。需区分会计波动、真实现金与受监管回报兑现，不能只看低GAAP P/E。',
'10/22收盘81.90美元除以全年调整后EPS中值3.97美元约20.63倍；低得多的GAAP TTM倍数受套期收益影响。',
'Q3已披露；本轮没有核实Dominion相关交易在比赛结束前可完成的确定时间，不能当作确定短期催化。',
'收益率上升、融资成本抬升、评级余量收窄、建设成本或并购负担增加，可能同时压低估值和每股现金回报。',
'若信用指标逼近/跌破评级要求、融资计划稀释超预期，或调整后指引下调，取消配置。',
'旧3%降至0%。不为“防守行业齐全”而引入新的利率与融资风险。',
'融资与评级余量、交易安排及投资回报证据改善，才讨论最多2%的替换仓；非自动恢复旧仓位。')

assert set(notes)==set(ORDER)==set(raw)
SOURCES=[]; ID={}
for t in ORDER:
 for f in raw[t]['facts']:
  url=f['source_url']
  if url not in ID: ID[url]=len(SOURCES)+1;SOURCES.append({'id':ID[url],'url':url,'date':f.get('source_date',''),'ticker':t})

CSS='''
:root{--ink:#152c3d;--muted:#526572;--blue:#12658b;--pale:#e8f1f5;--gold:#bc812e;--line:#d8e1e5;--red:#a53d3d;--green:#207262}*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:75px}body{margin:0;background:#f5f6f3;color:var(--ink);font:16px/1.8 "Segoe UI","Microsoft YaHei",sans-serif}a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}header{background:var(--ink);color:white;padding:38px max(24px,calc((100vw - 1160px)/2));}header a{color:#bde3f5}.eyebrow{font-size:12px;letter-spacing:2px;color:#afc6d2}h1{font-size:clamp(27px,4vw,43px);line-height:1.3;margin:14px 0}h2{font-size:27px;line-height:1.4;margin:4px 0 18px}h3{font-size:20px;margin:12px 0}p{margin:10px 0}nav{position:sticky;top:0;background:#fffef9;z-index:5;border-bottom:1px solid var(--line);padding:12px 20px;display:flex;gap:24px;overflow:auto;white-space:nowrap;font-size:14px}main{max-width:1208px;margin:auto;padding:24px}section{margin:20px 0 36px;padding:28px;background:white;border:1px solid var(--line);border-radius:14px}.label{font-size:12px;text-transform:uppercase;letter-spacing:1px;color:var(--blue);font-weight:700}.muted,small{color:var(--muted)}.callout{background:var(--pale);padding:18px 22px;border-left:4px solid var(--blue);border-radius:4px;margin:18px 0}.warn{background:#fff4e5;border-color:var(--gold)}.metrics,.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.metric,.tile{padding:18px;border:1px solid var(--line);border-radius:10px;background:#fbfcfb}.metric b{display:block;font-size:32px;color:var(--blue);line-height:1.3}.scroll{overflow:auto}table{width:100%;border-collapse:collapse;font-size:14px}th{text-align:left;background:#edf3f5;white-space:nowrap}td,th{padding:11px 12px;border-bottom:1px solid var(--line);vertical-align:top}tr:hover td{background:#fafcfd}.num{font-variant-numeric:tabular-nums;text-align:right;white-space:nowrap}.badge{display:inline-block;font-size:12px;padding:2px 9px;border-radius:20px;background:#e8f2ec;color:var(--green);margin:3px}.badge.wait{background:#fff0db;color:#85581e}.stock{border-top:1px solid var(--line);padding:24px 0}.stock:first-of-type{border-top:0}.stock-title{display:flex;justify-content:space-between;gap:20px;align-items:center}.stock-title h3{margin:0}.cols{display:grid;grid-template-columns:1fr 1fr;gap:24px}.key{font-weight:700;color:var(--blue)}.risk{color:var(--red)}details{border:1px solid var(--line);border-radius:8px;padding:12px 16px;margin:12px 0}summary{cursor:pointer;color:var(--blue);font-weight:600}li{margin:9px 0}.source-list{font-size:13px;overflow-wrap:anywhere}.source-list li{padding:8px 0;border-bottom:1px solid var(--line)}.weightbar{height:11px;border-radius:8px;background:#e5ecef;margin:5px 0}.weightbar i{display:block;height:100%;background:var(--blue);border-radius:8px}.rowbar{display:grid;grid-template-columns:140px 1fr 72px;align-items:center;gap:12px;margin:9px 0}.rowbar .weightbar i{background:#ad5858}.formula{font-family:Consolas,monospace;background:#edf3f5;padding:14px;overflow:auto}input,select{font:inherit;padding:8px;border:1px solid #a2b5c1;border-radius:5px;max-width:100%}footer{text-align:center;padding:25px;color:var(--muted);font-size:13px}.evidence{font-size:14px}.no-break{break-inside:avoid}@media(max-width:760px){main{padding:12px}section{padding:18px}.metrics,.grid,.cols{grid-template-columns:1fr}header{padding:25px 18px}nav{gap:18px}.stock-title{display:block}.rowbar{grid-template-columns:105px 1fr 60px}td,th{padding:9px}body{font-size:15px}}@media print{nav,button,input,select{display:none}body{background:white;font-size:11px}main{padding:0}section{break-inside:auto;border:0;padding:14px 0}header{color:var(--ink);background:white;padding:0}details{display:block}a{color:inherit}.grid,.metrics{grid-template-columns:repeat(3,1fr)}}
'''

def table(headers,rows):
 return '<div class="scroll"><table><thead><tr>'+''.join(f'<th>{E(h)}</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join(f'<td>{c}</td>' for c in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def paras(label,text):return f'<p><span class="key">{E(label)}：</span>{E(text)}</p>'
def fname(t):return t.replace('.','_')+'.html'
def source_links(t,prefix=''):
 seen=[]
 for f in raw[t]['facts']:
  n=ID[f['source_url']]
  if n not in seen:seen.append(n)
 return ' '.join(f'<a href="{prefix}#source-{n}">[{n}]</a>' for n in seen)
def stock_body(t,individual=False):
 n=notes[t]; q=quotes[t]; src=source_links(t,'../stock_deep_dive_risk_20261024.html' if individual else '')
 body=f'<div class="stock-title"><h3>{E(t)} · {E(n["name"])}</h3><div><span class="badge">周一 {START[t]}%</span><span class="badge wait">条件目标 {NEW[t]}%</span></div></div>'
 body+=f'<p class="muted">{E(n["role"])} · 旧目标 {OLD[t]}% · 10/22收盘 ${float(q["prev_close"]):.3f} · 10/23盘中 ${float(q["last_done"]):.3f}</p>'
 body+=paras('投资逻辑',n['case'])+'<ul>'+''.join(f'<li>{E(s)}</li>' for s in n['facts'])+'</ul>'
 body+=paras('盈利与现金质量',n['quality'])+paras('估值与已计价问题',n['valuation'])
 body+=f'<div class="cols"><div>{paras("催化与时间窗口",n["event"])}{paras("反方观点",n["bear"])}</div><div>{paras("失效条件",n["kill"])}{paras("仓位决定",n["decision"])}</div></div>'
 body+=f'<div class="callout">{paras("下一步需要的证据",n["proof"])}</div><p class="muted">相关原始文件：{src}。上述仓位与失效规则为本报告分析判断；所有证券WLS适格性仍需终端核验。</p>'
 body+='<details><summary>查看逐条事实、原始来源与尚未解决的证据缺口</summary><div class="evidence">'
 for f in raw[t]['facts']:
  body+=f'<p>{E(f["claim"])} <a href="{E(f["source_url"])}" target="_blank" rel="noopener">原始文件 ↗</a><br><small>文件日期 {E(f.get("source_date",""))} · 期间 {E(f.get("period",""))}</small></p>'
 body+='<p><b>尚未解决的事项</b></p><ul>'+''.join('<li>'+E(g)+'</li>' for g in raw[t].get('evidence_gaps',[]))+'</ul><p>底稿中的初次建仓资格疑点已由用户确认“已完成首次建仓”解决；其余数据、会计及WLS证据缺口继续保留。</p></div></details>'
 return body

def wrap(title,body,nav='',subtitle='15只个股复核 · 组合风险预算 · 2026-10-26条件建仓'):
 return f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)}</title><style>{CSS}</style></head><body><header><div class="eyebrow">BLOOMBERG TRADING CHALLENGE / RESEARCH NOTE 02</div><h1>{E(title)}</h1><p>{E(subtitle)}</p><p><small style="color:#bed0d9">报告日期：北京时间2026-10-24 · 历史风险数据截至10/22完整收盘 · 盘中报价采集于10/24 00:44左右</small></p></header>{nav}<main>{body}</main><footer>基于公开原始文件与Longbridge供应商快照的比赛研究。条件仓位设计，无交易执行；非收益承诺或最大损失保证。</footer></body></html>'

nav='<nav>'+''.join(f'<a href="#{id}">{name}</a>' for id,name in [('decision','结论'),('allocation','仓位'),('stocks','15只个股'),('expectations','财报门槛'),('risk','组合风险'),('execution','执行与回撤'),('sources','来源')])+'</nav>'
body='''<section id="decision"><div class="label">01 / Decision</div><h2>个股证据改变仓位，12%回撤容忍度约束节奏</h2><p>对上一轮优先方案B的15只股票分别核查后，建议把75%股票、25%现金的原目标，调整为<b>50%股票、50%现金的条件参考组合</b>；周一第一批仅使用20%，保留80%现金，之后按证据逐步决定是否增加。这里的现金比例以比赛允许保留相应现金为前提。</p><div class="metrics"><div class="metric"><b>15 → 11</b>逐股覆盖15只，条件目标中11只为正</div><div class="metric"><b>20% → 50%</b>周一试建比例 → 证据满足后的条件目标</div><div class="metric"><b>12%</b>用户确认的约组合回撤容忍度；非保证</div></div><div class="callout"><b>最重要的变化：</b>AMZN、ETN、TM、NEE暂不建仓；JNJ、WMT、XOM降低原目标；MSFT、GOOGL、ABBV等待财报。原因包括投资收益扭曲利润、高资本开支、估值、共同风险以及比赛窗口内缺少已核实催化。</div><p><b>这是一套风险预算参考，不是统计证明的最优组合。</b>没有为15只股票建立经验证的预期收益模型，也没有证明修订选股能提高比赛排名。较多现金减少下行敞口，也会在上涨市场拖累排名；部分防守股票估值并不低。</p><div class="callout warn"><b>已确认：</b>你已完成首次建仓，现有资产偏防守；本报告按可重新配置100%购买力规划，约可承受12%组合回撤，只做多、只买正股、单只不超过总净值20%。<br><b>仍待终端核对：</b>现有资产的实际市值及卖出结算、可用购买力、最低投资比例/现金规则、各证券WLS适格性。TM为ADR，资格需特别核验。本报告不是把现有防守资产直接当作现金；实际调仓先扣除保留持仓，避免重复计算。</div><p class="muted">范围为原B的全部15只股票；原C额外候选NVDA、TSM不在本次逐股覆盖范围。宏观背景沿用<a href="../2026-10-23/global_market_positioning_20261026.html">上一轮全球市场报告</a>，本轮重点是在公司证据层面验证或推翻原仓位。</p></section>'''

rows=[]
for t in ORDER:
 n=notes[t];action='条件保留' if NEW[t] else '暂不建仓'
 rows.append([f'<a href="stocks/{fname(t)}">{E(t)} · {E(n["name"])}</a>',str(OLD[t])+'%',str(START[t])+'%',str(NEW[t])+'%',E(action),f'<a href="#stock-{t.replace(".","_")}">查看分析</a>'])
rows.append(['现金','25%','80%','50%','取决于比赛现金规则','不与现有持仓重复计算'])
body+='<section id="allocation"><div class="label">02 / Allocation</div><h2>所有权重均占组合总净值</h2>'+table(['证券','原B目标','周一第一批','修订条件目标','决定','分析'],rows)
body+='''<p>20%是用户规定的<b>单只股票合规上限</b>，不是仓位目标。当前最大条件单名为PG 7%；股票仓位本身也只是总净值的50%。AMZN/ETN/TM/NEE之后若重新引入，须替换已有风险预算，不能直接叠加。</p><details><summary>用假设净值查看金额与参考股数（仅计算器）</summary><p>净值 <input id="nav-input" type="number" value="100000" min="0" step="1000" aria-label="假设美元净值"> 美元　<select id="plan-input" aria-label="选择方案"><option value="starter">周一20%方案</option><option value="target">条件50%方案</option></select></p><p class="muted">默认10万美元只是示例，并非你的账户规模。用盘中参考价向下取整，不代表可成交价或比赛订单；实际数量须按新报价、现有保留仓位及购买力重算。</p><div id="sizing"></div></details></section>'''

body+='<section id="stocks"><div class="label">03 / Individual underwriting</div><h2>15只股票：逐一说明持有理由、反方观点和退出条件</h2><p>各公司现金流期间不同，不将其直接排名。估值段明确使用10/22收盘或10/23盘中价格；调整后指引倍数、GAAP TTM倍数及现金收益率是不同口径。没有足够证据的公司保留估值缺口，不制造目标价。</p>'
for t in ORDER:
 body+=f'<article class="stock" id="stock-{t.replace(".","_")}">{stock_body(t)}<p><a href="stocks/{fname(t)}">打开 {E(t)} 独立研究页 →</a></p></article>'
body+='</section>'

consrows=[]
bench={'MSFT':'公司收入898.5—909.5亿美元；Azure固定汇率约45%','GOOGL':'拆开投资收益、并购与经营增长，不只比较GAAP EPS','AMZN':'公司收入1970—2020亿美元，经营利润225—265亿美元；预期已略高于收入上沿','ABBV':'10/5更新后调整EPS3.73—3.77；先对齐normalized与公司定义','XOM':'10/16因素桥已公开；不是完整盈利预测','CVX':'核查营运资本、TCO分配与并表贡献','ETN':'调整EPS3.46—3.56；预期已接近上沿'}
for t in ['MSFT','GOOGL','AMZN','ABBV','XOM','CVX','ETN']:
 c=CONS[t]['next']; vals={x['key']:float(x['estimate']) for x in c['details'] if 'estimate' in x}
 consrows.append([E(t),E(c['period_text']),f'{vals["revenue"]/1e9:.3f}',f'{vals.get("eps",0):.4f}',f'{vals.get("normalized_eps",0):.4f}',E(bench[t])])
body+='<section id="expectations"><div class="label">04 / Expectations hurdle</div><h2>好公司、好业绩与好交易是三件不同的事</h2><p>下表为Longbridge下一未披露期间的供应商一致预期，采集记录截至10/23 16:46 UTC左右；没有独立分析师修订时间戳，因此仅作为财报核对参考。收入单位为<b>十亿美元</b>，EPS为美元/股。供应商EPS及normalized定义需与公司GAAP/调整后口径分别核对，不默认可互换。</p>'+table(['证券','财季','预期收入','EPS供应商口径','normalized EPS','公司门槛/解释'],consrows)
body+='''<p><b>拒绝使用的字段：</b>BRK供应商“下一期”仍指向已过去期间，已剔除；微软供应商异常FCF字段用公司现金流表重新勾稽；缺少期间、分析师数量为0的远期EPS不作为估值依据。TM的美元EPS未完成ADR/日元换算；银行与部分公用事业现金/净债字段缺失，不填成0。</p><p>市场已经知道的利好不自动等于预期差。AMZN与ETN的收入/EPS预期接近或超过公司指引上沿，意味着仅完成指引也可能不能支持股价上涨。WMT下一次财报11/19、JNJ战略回顾12/8在比赛结束后，不能被包装成短赛程催化。</p></section>'''

riskrows=[]
labels={'原B_75':'原B：75%股票','原B同比缩到50':'原B同比缩至50%','修订B_50':'修订：50%股票','修订B周一20':'周一：20%股票'}
for k,r in R['risk'].items():
 riskrows.append([E(labels[k]),f'{r["windows"]["60"]["vol"]:.2f}%',f'{r["windows"]["120"]["vol"]:.2f}%',f'{r["windows"]["252"]["vol"]:.2f}%',f'{r["windows"]["60"]["correlation_shift_vol"]:.2f}%',f'{r["windows"]["60"]["all_positive_one_vol"]:.2f}%'])
body+='<section id="risk"><div class="label">05 / Portfolio risk</div><h2>先把公司证据接回全球市场框架</h2>'
body+=table(['全球驱动','哪些股票可能一起受影响','如何改变仓位决定'],[
 ['油价、炼油价差与通胀','XOM/CVX直接；WMT/PG等另受成本与消费影响','能源只作部分情景缓冲。衰退或供给恢复时油股可能与股票组合同时跌，因此先把油企财报前合计压至3%。'],
 ['实际收益率与融资条件','MSFT/GOOGL/AMZN/ETN/NEE的资本投入与长久期估值；JPM另受曲线和信用影响','利率下降不自动等于利好：若是衰退引起，盈利和信用可能恶化。NEE不因公用事业标签就获得仓位。'],
 ['增长、就业与信用','JPM、BRK实业与保险、WMT、TM，以及能源需求','信用成本、现金和经营利润比GAAP净利润增速更有解释力；12%风险预算为全组合而非每个主题分别使用。'],
 ['AI资本开支与融资回报','MSFT/GOOGL/AMZN/ETN','平台与设备不是独立押注：条件目标合计8%，财报前0%；AMZN/ETN重新引入必须替换组内预算。'],
 ['美元、日元与央行分歧','TM ADR、跨国消费和科技；能源与利率也交叉传导','美元报价不消除外汇风险；TM营业利润依赖弱日元假设，不能只凭地域分散就配置。']])
body+='<h3>同等股票仓位下的历史风险比较</h3><p>使用截至10/22完整收盘的历史价格；60日窗口为7/30—10/22。下表为组合<b>年化波动率敏感性</b>，不是预测最大回撤。现金收益按0计；以加权对数收益协方差近似，未计费用、税务、分红再投资及成交偏差。</p>'+table(['组合','60日样本','120日样本','252日样本','60日相关性上移','60日相关系数全为+1'],riskrows)
body+='''<div class="callout warn"><b>修订组合并非全面占优：</b>同样50%股票时，修订组合60日样本波动5.35%，高于按比例缩小的旧组合4.79%；但相关性上移敏感性9.02%，略低于旧组合9.39%。这说明仓位调整是在不同风险之间取舍，不能宣称已经得到更高收益或更低一切风险的组合。</div><p>相关性压力采用 <code>C′ = 0.5 × C样本 + 0.5 × 全1矩阵</code>，保持各股票样本波动率不变，避免只依赖平静期低相关。全+1只是更强的同向敏感性，仍不是最大损失界限。</p>'''
scenarios=list(R['stress_vectors'])
stressrows=[]
for s in scenarios:
 stressrows.append([E(s)]+[f'{R["risk"][k]["scenario"][s]:+.2f}%' for k in labels])
body+='<h3>人为压力情景，不赋予概率</h3>'+table(['情景']+[labels[k] for k in labels],stressrows)
body+='''<p>压力向量是分析假设，完整逐股冲击见<a href="risk_comparison.json">risk_comparison.json</a>。未受冲击股票在情景中按0变动处理，可能低估二阶传导。这些情景不是穷尽风险，也不是VaR、预期短缺或最大回撤预测。</p><div class="callout"><b>衰退情景改善的拆分：</b>原75%组合损失14.70%；只把原组合同比缩到50%，损失已降至9.80%；更换权重后为9.32%。因此总改善5.38个百分点中，<b>4.90个百分点来自降低股票仓位，只有0.48个百分点来自同等敞口下的成分调整</b>。这不能作为选股产生超额收益的证明。</div>'''
body+='<h3>12%容忍度如何进入设计</h3><p>修订50%组合在上述衰退假设下损失9.32%，距12%留2.68个百分点余量，但未知事件、跳空、流动性与模型误差仍可能突破12%。把12÷9.32机械放大到约64.4%股票会消耗这部分余量，本报告不建议因此直接加仓。周一20%组合相同情景损失3.65%，用于财报密集周的初步暴露。</p>'
grows=[]
for g,vals in R['groups'].items():
 grows.append([E(g),f'{vals["原B_75"]:.1f}%',f'{vals["原B同比缩到50"]:.1f}%',f'{vals["修订B_50"]:.1f}%',f'{vals["修订B周一20"]:.1f}%'])
body+='<h3>股票数不等于独立风险数</h3>'+table(['共同驱动组','原B75','原B缩至50','修订50','周一20'],grows)
body+='''<p>金融/综合组在修订组合占总净值12%，即股票资金的24%；周一为7%总净值、占股票资金35%。这是仍需注意的集中，并没有因为持有多个行业而消失。能源8%同时承受商品价格与10/30财报；AI组8%共享资本支出周期。分组为观察视角，未覆盖所有交叉风险，不能简单当作互斥行业加总。</p><p><b>严重单名敏感性：</b>JPM 6%仓位若跌30%，损失净值1.8%；XOM+CVX合计8%若同跌25%，损失2%；WMT 3%若仅倍数收缩导致约24%下跌，损失约0.72%。一般单名冲击假设与严重敏感性不同，均不是最大损失。若选择单名严重事件最多损失1.5%净值的更严预算，JPM需降至5%，差额留现金，不能声称当前6%同时满足该预算。</p></section>'''

body+='''<section id="execution"><div class="label">06 / Execution & drawdown</div><h2>20%到50%靠证据解锁，回撤限制提前介入</h2><p>用户允许重新配置全部购买力，因此下面描述目标组合与调仓方法；不是确认当前账户已空仓。先核对实际防守资产、未成交订单、可用资金与结算，再从目标金额中扣除拟保留仓位。所有新买证券必须在终端验证WLS、最低投资比例与交易限制。</p><div class="callout warn"><b>下周宏观事件与公司财报重叠：</b><a href="https://www.federalreserve.gov/newsevents/2026-october.htm">FOMC 10/27—28会议</a>，决议对应北京时间10/29 02:00、发布会02:30；<a href="https://www.bea.gov/news/schedule/full">BEA日程</a>列示Q3 GDP初值与9月个人收入支出/PCE于10/29 08:30 ET，即北京时间20:30。另有ECB 10/28—29及BOJ 10/29—30会议。沿用上一轮已读取官方日历，执行前再核公告。不能在公司业绩好于预期时忽略同时发生的政策和通胀冲击。</div>'''
body+=table(['阶段','参考动作','解锁条件/约束'],[
 ['10/26周一','第一批20%：JPM4、JNJ3、PG3、BRK.B3、XOM2、WMT2、LMT2、CVX1；现金80%','北京时间21:30美股常规开盘；先观察15—30分钟，分批限价。若重大新闻改变逻辑或价格使估值失效，不为完成权重下单。现金比例必须符合比赛规则。'],
 ['10/28—10/30财报集群','MSFT、GOOGL、ABBV财报前保持0；油企合计先3%','比较公司指引、同口径预期、现金质量及下一季展望。财报后先重新估值，再分批建仓；不得因大涨追足目标。'],
 ['事件核查后','仅在证据成立时向50%条件目标靠近','新增30%中：MSFT/GOOGL/ABBV合计11%；油企额外5%；其他已披露公司额外14%。三部分均可只执行一部分，不需要等全部公司财报，也不是到日期自动执行。'],
 ['11/3及之后','ETN等观察名单若重新引入，替换同类预算','不在50%股票之上直接叠加。比赛结束前缺少兑现窗口的长期逻辑权重从严。'],
 ['11/13结束前','核对终端最终计价、成交截止与结算规定','不假设能够在最后一刻按显示价格全部退出；具体执行与规则以终端/当届手册为准。']])
body+='''<p>若同一篮子股票上涨5%，在现金收益按0的简化下，50%股票约贡献2.5%组合收益，原75%约贡献3.75%，相差1.25个百分点。因此修订版适合“先控制比赛回撤、保留后续购买力”，不能保证排名更好。若比赛现金限制不允许50%或80%现金，须重做股票替代与压力测试；不能把现金机械塞进单只所谓防守股。</p><h3>以净值高水位计算组合回撤</h3><div class="formula">回撤 = 当前组合净值 ÷ 本轮起始以来净值高水位 − 1<br>净值包含全部现有/新持仓、现金、已实现及未实现盈亏与交易成本；外部资金变动需调整。</div>'''
body+=table(['回撤/触发','建议动作（分析规则）','目的与限制'],[
 ['约4%','暂停尚未触发的加仓；逐项分解油价、利率、信用与财报损失','先判断是共同风险还是个股逻辑失效，不以价格下跌作为补仓理由。'],
 ['约6%','重新运行压力测试；优先削减失效逻辑与同类重复风险，参考将股票降至不高于35%','需结合当时现金规则、持仓与跳空；不是单纯对所有持仓同比卖出。'],
 ['约8%','进入资本保全模式，股票参考降至20%以内；取消财报前新增风险','在12%容忍度之前留操作余量；价格跳空可能使实际成交更差。'],
 ['约10%','停止新增；能交易且符合规则时，将风险持仓压至最低必要水平，现金目标90%以上','比赛最低投资比例若不允许，应先解决规则约束；不能保证该动作把损失锁在12%内。'],
 ['触及/超过12%','认定风险预算已被突破，记录原因并重新决定是否继续承担风险','12%是用户容忍度，不是止损单或模型能够保证的上限。']])
body+='''<p><b>个股层面：</b>公司指引下调、法律/信用事件、现金质量恶化等基本面失效可早于组合阈值处理；入场后收盘较成本回落约6%触发重新核查，不自动当作固定卖点，也不自动摊低。财报跳空、停牌与限价未成交会突破价格阈值。</p><p><b>每日收盘复核：</b>总净值回撤、各股及共同风险权重、财报前风险金额、下一日催化、可用资金与未成交订单。对上涨导致的权重漂移同样复核；用户20%合规上限不能靠“起初买得少”保证持续满足。</p></section>'''

body+='<section id="sources"><div class="label">07 / Evidence & reproducibility</div><h2>事实、估值假设与仓位判断分开保存</h2><p>优先采用公司财报、SEC文件、IR日历及管理层原始材料；Longbridge用于行情、历史风险与供应商一致预期。Bloomberg公开网页为背景阅读，受机器人验证限制的文章正文没有被当作已读取证据。没有使用付费终端独有数据来冒充当前已验证事实。</p>'
body+='''<p><b>快照边界：</b>10/23纽约12:44左右的行情仍属周五盘中；本报告没有周五完整收盘。风险样本截止10/22；财务资料对应各自财季，不把不同时点净债务横比成实时杠杆排名。报价、共识与会计指引也没有被当作同一口径。</p><p><b>研究底稿：</b><a href="lane_growth_industrial.md">科技/工业6只</a> · <a href="lane_health_consumer.md">医疗/消费4只</a> · <a href="lane_energy_finance_japan.md">能源/金融/日本5只</a>。底稿保留较早假设，最终权重与已确认用户约束以本报告、risk_comparison.json及CSV为准。</p><p><b>复现文件：</b><a href="revised_stock_allocations.csv">仓位CSV</a> · <a href="risk_comparison.json">完整风险向量与结果</a> · <a href="risk_analysis.py">风险计算脚本</a> · <a href="source_register.json">原始来源索引</a> · <a href="validation.json">验证记录</a>。风险脚本依赖上一轮目录的原始价格；打包版保留该相对目录结构。</p><p><b>尚未完成的研究：</b>没有15只股票统一的可审计NTM估值、完整DCF、期权隐含事件幅度或预期收益模型，也未获得当日终端WLS成员证明。因此不声称找到最佳股票、目标收益率或保证符合全部比赛条件。</p><ol class="source-list">'''
for s in SOURCES:
 body+=f'<li id="source-{s["id"]}"><b>[{s["id"]}] {E(s["ticker"])}</b> · 文件日期 {E(s["date"])}<br><a href="{E(s["url"])}" target="_blank" rel="noopener">{E(s["url"])}</a></li>'
body+='</ol></section>'

payload={t:{'name':notes[t]['name'],'price':float(quotes[t]['last_done']),'starter':START[t],'target':NEW[t]} for t in ORDER}
script='''<script>const data=PAYLOAD;function size(){const nav=Number(document.getElementById('nav-input').value);const plan=document.getElementById('plan-input').value;let out='<div class="scroll"><table><tr><th>证券</th><th>目标金额 / USD</th><th>参考股数 / 向下取整</th></tr>';for(const [t,d]of Object.entries(data)){const v=nav*d[plan]/100;out+=`<tr><td>${t}</td><td>${v.toLocaleString(undefined,{maximumFractionDigits:2})}</td><td>${Math.floor(v/d.price)}</td></tr>`}out+='</table></div>';document.getElementById('sizing').innerHTML=out}document.getElementById('nav-input').addEventListener('input',size);document.getElementById('plan-input').addEventListener('change',size);size();</script>'''.replace('PAYLOAD',json.dumps(payload,ensure_ascii=False))
main=wrap('从15只个股，重建组合风险预算',body,nav)
main=main.replace('</body>',script+'</body>')
(P/'stock_deep_dive_risk_20261024.html').write_text(main,encoding='utf-8')
(P/'stocks').mkdir(exist_ok=True)
for t in ORDER:
 sub='<section><p><a href="../stock_deep_dive_risk_20261024.html#allocation">← 返回组合与风险报告</a></p><div class="callout warn">全部权重占组合总净值；以可重新配置全部购买力设计，约12%组合回撤容忍度。周一仓位与财报后条件目标不同。没有下单，WLS及现金规则仍需终端确认。</div>'+stock_body(t,True)+'</section>'
 (P/'stocks'/fname(t)).write_text(wrap(f'{t} · {notes[t]["name"]} 个股研究',sub,subtitle=notes[t]['role']),encoding='utf-8')
(P/'source_register.json').write_text(json.dumps(SOURCES,ensure_ascii=False,indent=2),encoding='utf-8')
(P/'stock_research_synthesis.json').write_text(json.dumps({'user_update':R['user_constraints'],'stocks':notes,'source_register':SOURCES},ensure_ascii=False,indent=2),encoding='utf-8')

# Preserve the original report as a dated snapshot, but make the stock-only update visible.
old_path=P.parent/'2026-10-23'/'global_market_positioning_20261026.html'
oldhtml=old_path.read_text(encoding='utf-8')
marker='stock-only-update-20261024'
if marker not in oldhtml:
 banner='<aside id="'+marker+'" style="padding:20px;background:#fff1cf;color:#152c3d;border-bottom:3px solid #bc812e;font:16px/1.8 sans-serif"><b>2026-10-24更新：</b>用户确认仅做多正股、单名≤20%、已完成首次建仓并按全部购买力重新配置，回撤容忍度约12%。<a style="color:#12658b" href="../2026-10-24/stock_deep_dive_risk_20261024.html">请优先阅读15只个股与修订风险报告 →</a> 本页保留原始宏观研究；其中ETF执行方案不适用于该账户，原B权重已被新版条件参考取代。</aside>'
 oldhtml=re.sub(r'(<body[^>]*>)',lambda m:m.group(1)+banner,oldhtml,count=1)
 old_path.write_text(oldhtml,encoding='utf-8')

readme='''# 2026-10-24 个股研究与组合风险复核

入口：stock_deep_dive_risk_20261024.html；stocks/ 中15只股票均有独立研究页。

用户最新确认：已完成首次建仓、现有防守资产；按全部购买力可重新配置规划，约12%组合回撤容忍度。只做多、只买正股、单名最多20%总净值。WLS及现金/最低投资比例仍需终端核对。

参考：周一20%股票/80%现金；条件目标50%股票/50%现金。不是概率最优组合或交易执行。旧B为75%股票；风险表额外比较旧B同比降到50%，以分开仓位效应与成分效应。

行情：10/23纽约12:44左右盘中；风险历史截至10/22完整收盘。没有周五收盘。

复现：安装 numpy pandas，执行 python risk_analysis.py，再执行 python build_stock_report.py。risk_analysis.py依赖同级 ../2026-10-23/analysis.json、stock_raw.json、market_raw.json。ZIP保留两日期目录结构。

sources、quotes、consensus、财务快照是本轮采集的审计材料，不是终端WLS证明。bs_snapshot_final.json、consensus_records_final.json为最终成功快照；失败或被替代的provider原始尝试不纳入交付包。

lane底稿与原始agent结论保留研究过程；最终用户约束、仓位与结论以HTML、risk_comparison.json、revised_stock_allocations.csv为准。
'''
(P/'README.md').write_text(readme,encoding='utf-8')
print(json.dumps({'report_chars':len(main),'stock_pages':len(ORDER),'primary_source_urls':len(SOURCES)},ensure_ascii=False))
