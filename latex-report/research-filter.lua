local function addfig(path, caption, width)
  return pandoc.Para({
    pandoc.Image({pandoc.Str(caption)}, path, caption, pandoc.Attr("", {}, {{"width", width or "92%"}}))
  })
end

function Header(el)
  local s = pandoc.utils.stringify(el.content)
  if s:match("量、价、期限") or s:match("季度运营指标") then
    return {el, addfig("latex-report/figures/glp_ops.png", "图：出租率与租金变化（研究整理）", "94%")}
  elseif s:match("五个披露项目") or s:match("项目运营对比") then
    return {el, addfig("latex-report/figures/glp_projects.png", "图：底层项目运营分化（研究整理）", "94%")}
  elseif s:match("收入、现金流") or s:match("收入趋势与现金流质量") then
    return {el, addfig("latex-report/figures/glp_cash.png", "图：季度收入与可供分配金额（研究整理）", "94%")}
  elseif s:match("季度与半年度指标矩阵") then
    return {el, addfig("latex-report/figures/huaxia_ops.png", "图：出租率与有效租金的分化（研究整理）", "94%")}
  elseif s:match("租户集中度") then
    return {el, addfig("latex-report/figures/huaxia_tenants.png", "图：租户集中度（依据披露数据整理）", "88%")}
  elseif s:match("租金敏感性分析") then
    return {el, addfig("latex-report/figures/huaxia_sensitivity.png", "图：租金压力情景下的分派率（模型测算）", "88%")}
  elseif s:match("投资摘要") or s:match("投资摘要：") then
    return {el, addfig("latex-report/figures/sino_irr.png", "图：不同情景下的持有到期 IRR（模型测算）", "90%")}
  elseif s:match("现金流预测与情景测算") then
    return {el, addfig("latex-report/figures/sino_scenarios.png", "图：2028 年租约重定价情景（模型测算）", "90%")}
  end
  return el
end
