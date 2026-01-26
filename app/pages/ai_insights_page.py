"""
AI洞察页面模块
"""

import streamlit as st
import pandas as pd
from typing import Dict, Optional, Any


class AIInsightsPage:
    """AI洞察页面组件"""
    
    def __init__(self, config):
        """初始化AI洞察页面"""
        self.config = config
    
    def render(self):
        """渲染AI洞察页面"""
        # 现代化页面标题
        st.markdown("""
        <div class="fade-in" style="text-align: center; padding: 1rem 0 2rem 0;">
            <h1 style="font-size: 2.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">
                🤖 AI洞察
            </h1>
            <p style="color: #6c757d; font-size: 1.1rem;">
                人工智能驱动的专业投资建议
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if not self.config.llm_api_key:
            st.error("❌ 未配置LLM API密钥，无法使用AI功能")
            st.info("请在环境变量或.env文件中配置LLM_API_KEY")
            return
        
        if not st.session_state.analysis_results:
            st.warning("⚠️ 请先运行分析以获取AI洞察")
            return
        
        # 创建选项卡
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 技术分析", 
            "📈 基本面分析", 
            "🔍 单股分析", 
            "🌐 市场洞察"
        ])
        
        with tab1:
            self._render_technical_analysis()
        
        with tab2:
            self._render_fundamental_analysis()
            
        with tab3:
            self._render_single_stock_analysis()
            
        with tab4:
            self._render_market_insights()
    
    def _render_technical_analysis(self):
        """渲染技术分析标签页"""
        st.markdown("### 📊 技术分析")
        st.markdown("基于技术指标的股票池综合分析")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            analysis_scope = st.selectbox(
                "选择分析范围",
                ["股票池综合分析", "板块轮动分析", "趋势强度分析"],
                index=0,
                key="tech_analysis_scope"
            )
        
        with col2:
            st.markdown("###")  # 空行对齐
            generate_btn = st.button(
                "🤖 生成技术分析", 
                type="primary", 
                key="generate_tech_analysis_btn",
                use_container_width=True
            )
        
        if generate_btn:
            with st.spinner("AI正在进行技术分析..."):
                try:
                    if st.session_state.analyzer:
                        if analysis_scope == "股票池综合分析":
                            ai_analysis = st.session_state.analyzer.generate_pool_ai_analysis()
                        elif analysis_scope == "板块轮动分析":
                            ai_analysis = st.session_state.analyzer.generate_sector_rotation_analysis()
                        else:  # 趋势强度分析
                            ai_analysis = st.session_state.analyzer.generate_trend_strength_analysis()
                        
                        if ai_analysis:
                            st.markdown("### 📝 技术分析报告")
                            st.markdown(ai_analysis)
                        else:
                            st.error("技术分析生成失败")
                    else:
                        st.error("分析器未初始化")
                except Exception as e:
                    st.error(f"技术分析失败: {str(e)}")
    
    def _render_fundamental_analysis(self):
        """渲染基本面分析标签页"""
        st.markdown("### 📈 基本面分析")
        st.markdown("基于财务数据和宏观经济的深度分析")
        
        # 分析选项配置
        col1, col2 = st.columns(2)
        
        with col1:
            fundamental_type = st.selectbox(
                "基本面分析类型",
                [
                    "财务健康度分析",
                    "估值分析", 
                    "盈利能力分析",
                    "成长性分析",
                    "行业对比分析"
                ],
                index=0,
                key="fundamental_type_selector"
            )
        
        with col2:
            time_period = st.selectbox(
                "分析时间周期",
                ["最近一年", "最近三年", "最近五年"],
                index=0,
                key="fundamental_time_period"
            )
        
        # 高级选项
        with st.expander("🔧 高级分析选项", expanded=False):
            col3, col4 = st.columns(2)
            
            with col3:
                include_macro = st.checkbox("包含宏观经济分析", value=True, key="fundamental_include_macro")
                include_industry = st.checkbox("包含行业分析", value=True, key="fundamental_include_industry")
            
            with col4:
                include_competitors = st.checkbox("包含竞争对手分析", value=False, key="fundamental_include_competitors")
                risk_assessment = st.checkbox("深度风险评估", value=True, key="fundamental_risk_assessment")
        
        # 生成分析按钮
        if st.button("🔬 生成基本面分析", type="primary", key="generate_fundamental_btn", use_container_width=True):
            with st.spinner("AI正在进行基本面分析..."):
                try:
                    if st.session_state.analyzer:
                        # 收集分析参数
                        analysis_params = {
                            'type': fundamental_type,
                            'time_period': time_period,
                            'include_macro': include_macro,
                            'include_industry': include_industry,
                            'include_competitors': include_competitors,
                            'risk_assessment': risk_assessment
                        }
                        
                        ai_analysis = st.session_state.analyzer.generate_fundamental_analysis(analysis_params)
                        
                        if ai_analysis:
                            st.markdown("### 📊 基本面分析报告")
                            
                            # 使用可展开的区域显示不同部分
                            sections = self._parse_fundamental_analysis(ai_analysis)
                            
                            for section_title, section_content in sections.items():
                                with st.expander(f"📋 {section_title}", expanded=True):
                                    st.markdown(section_content)
                        else:
                            st.error("基本面分析生成失败")
                    else:
                        st.error("分析器未初始化")
                except Exception as e:
                    st.error(f"基本面分析失败: {str(e)}")
        
        # 添加说明信息
        st.info("""
        💡 **基本面分析说明**
        - 财务健康度：资产负债状况、现金流分析
        - 估值分析：PE、PB、PEG等估值指标分析
        - 盈利能力：ROE、ROA、毛利率等指标
        - 成长性：营收增长率、利润增长率分析
        - 行业对比：与同行业公司的比较分析
        """)
    
    def _render_single_stock_analysis(self):
        """渲染单股分析标签页"""
        st.markdown("### 🔍 单股深度分析")
        st.markdown("选择股票进行AI驱动的深度分析，获得专业的投资建议")
        
        if not st.session_state.analysis_results:
            st.warning("⚠️ 请先运行股票分析")
            return
        
        # 创建两列布局
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 股票选择
            selected_stock = st.selectbox(
                "📊 选择分析的股票",
                list(st.session_state.analysis_results.keys()),
                key="single_stock_selector",
                help="从已分析的股票中选择一只进行深度分析"
            )
            
            # 分析深度选择
            analysis_depth = st.radio(
                "🎯 分析深度",
                ["快速分析", "深度分析", "全面评估"],
                index=1,
                key="analysis_depth",
                help="选择分析深度：快速分析适合短期交易，深度分析适合中期投资，全面评估适合长期投资"
            )
            
            # 分析类型选择
            analysis_type = st.multiselect(
                "📋 分析类型",
                ["技术分析", "基本面分析", "风险评估", "投资建议", "市场情绪"],
                default=["技术分析", "投资建议"],
                key="analysis_type_multiselect",
                help="选择要包含的分析类型"
            )
        
        with col2:
            # 显示选中股票的基本信息
            if selected_stock:
                st.markdown("#### 📈 股票信息")
                stock_data = st.session_state.analysis_results.get(selected_stock)
                if stock_data and 'data' in stock_data:
                    df = stock_data['data']
                    if not df.empty:
                        current_price = df.iloc[-1]['close']
                        price_change = df.iloc[-1]['close'] - df.iloc[-2]['close'] if len(df) > 1 else 0
                        change_pct = (price_change / df.iloc[-2]['close'] * 100) if len(df) > 1 and df.iloc[-2]['close'] != 0 else 0
                        
                        st.metric(
                            "当前价格",
                            f"¥{current_price:.2f}",
                            f"{change_pct:+.2f}%"
                        )
                        
                        # 显示技术指标
                        st.markdown("**技术指标**")
                        if 'RSI' in df.columns:
                            rsi = df.iloc[-1]['RSI']
                            st.write(f"RSI: {rsi:.1f}")
                        if 'MACD' in df.columns:
                            macd = df.iloc[-1]['MACD']
                            st.write(f"MACD: {macd:.3f}")
        
        # 高级选项
        with st.expander("🔧 高级分析选项", expanded=False):
            col3, col4 = st.columns(2)
            
            with col3:
                include_news = st.checkbox("包含新闻分析", value=False, key="single_stock_include_news")
                include_sentiment = st.checkbox("包含情绪分析", value=True, key="single_stock_include_sentiment")
                include_competitors = st.checkbox("包含竞争对手分析", value=False, key="single_stock_include_competitors")
            
            with col4:
                risk_tolerance = st.selectbox(
                    "风险偏好",
                    ["保守型", "稳健型", "积极型", "激进型"],
                    index=1,
                    key="risk_tolerance"
                )
                investment_horizon = st.selectbox(
                    "投资周期",
                    ["短期(1-3个月)", "中期(3-12个月)", "长期(1-3年)"],
                    index=1,
                    key="investment_horizon"
                )
        
        # 分析历史记录
        if 'single_stock_analysis_history' not in st.session_state:
            st.session_state.single_stock_analysis_history = {}
        
        # 显示历史分析
        if selected_stock in st.session_state.single_stock_analysis_history:
            st.markdown("#### 📚 历史分析记录")
            history = st.session_state.single_stock_analysis_history[selected_stock]
            
            for i, (timestamp, analysis) in enumerate(history[-3:]):  # 显示最近3次分析
                with st.expander(f"📅 {timestamp} - {analysis['depth']}", expanded=False):
                    st.markdown(analysis['content'])
                    if st.button(f"🗑️ 删除", key=f"delete_history_{i}"):
                        history.pop(i)
                        st.rerun()
        
        # 生成分析按钮
        col5, col6 = st.columns([1, 1])
        
        with col5:
            generate_btn = st.button(
                "🔍 生成深度分析", 
                type="primary", 
                key="generate_single_analysis_btn",
                use_container_width=True
            )
        
        with col6:
            if st.button("💾 保存当前分析", key="save_analysis_btn", use_container_width=True):
                if 'current_single_stock_analysis' in st.session_state:
                    self._save_analysis_to_history(selected_stock)
                    st.success("✅ 分析已保存到历史记录")
                else:
                    st.warning("⚠️ 请先生成分析")
        
        if generate_btn:
            with st.spinner(f"🤖 AI正在分析 {selected_stock}..."):
                try:
                    if st.session_state.analyzer:
                        stock_data = st.session_state.analysis_results.get(selected_stock)
                        if stock_data:
                            # 构建分析参数
                            analysis_params = {
                                'depth': analysis_depth,
                                'types': analysis_type,
                                'include_news': include_news,
                                'include_sentiment': include_sentiment,
                                'include_competitors': include_competitors,
                                'risk_tolerance': risk_tolerance,
                                'investment_horizon': investment_horizon
                            }
                            
                            ai_analysis = st.session_state.analyzer.generate_single_stock_analysis(
                                selected_stock, stock_data, analysis_depth
                            )
                            
                            if ai_analysis:
                                # 保存当前分析到session state
                                st.session_state.current_single_stock_analysis = {
                                    'stock': selected_stock,
                                    'depth': analysis_depth,
                                    'content': ai_analysis,
                                    'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                                }
                                
                                # 显示分析结果
                                st.markdown(f"### 📈 {selected_stock} 深度分析报告")
                                
                                # 添加分析摘要
                                st.markdown("#### 📋 分析摘要")
                                summary_col1, summary_col2, summary_col3 = st.columns(3)
                                
                                with summary_col1:
                                    st.metric("分析深度", analysis_depth)
                                with summary_col2:
                                    st.metric("分析类型", f"{len(analysis_type)}项")
                                with summary_col3:
                                    st.metric("风险偏好", risk_tolerance)
                                
                                # 显示详细分析
                                st.markdown("#### 📊 详细分析")
                                
                                # 使用可展开的区域显示分析内容
                                analysis_sections = self._parse_single_stock_analysis(ai_analysis)
                                
                                for section_title, section_content in analysis_sections.items():
                                    with st.expander(f"📋 {section_title}", expanded=True):
                                        st.markdown(section_content)
                                
                                # 添加操作按钮
                                st.markdown("#### 🔧 操作")
                                action_col1, action_col2, action_col3 = st.columns(3)
                                
                                with action_col1:
                                    if st.button("📊 查看图表", key="view_charts_btn"):
                                        st.session_state.page = "📈 图表"
                                        st.rerun()
                                
                                with action_col2:
                                    if st.button("📝 导出报告", key="export_report_btn"):
                                        self._export_analysis_report(selected_stock, ai_analysis)
                                
                                with action_col3:
                                    if st.button("🔄 重新分析", key="reanalyze_btn"):
                                        st.rerun()
                                
                            else:
                                st.error("❌ 单股分析生成失败")
                        else:
                            st.error(f"❌ 未找到 {selected_stock} 的分析数据")
                    else:
                        st.error("❌ 分析器未初始化")
                except Exception as e:
                    st.error(f"❌ 单股分析失败: {str(e)}")
        
        # 添加使用说明
        st.info("""
        💡 **单股分析使用说明**
        - **快速分析**：适合短期交易，重点关注技术指标和短期趋势
        - **深度分析**：适合中期投资，包含基本面推测和风险评估
        - **全面评估**：适合长期投资，提供多维度综合分析和投资策略
        - 分析结果会自动保存到历史记录，方便后续查看和对比
        """)
    
    def _render_market_insights(self):
        """渲染市场洞察标签页"""
        st.markdown("### 🌐 市场洞察")
        st.markdown("宏观市场趋势和投资机会分析")
        
        insight_type = st.selectbox(
            "洞察类型",
            ["市场趋势预测", "热点板块分析", "资金流向分析", "情绪指标分析"],
            index=0,
            key="market_insight_type"
        )
        
        if st.button("📈 生成市场洞察", type="primary", key="generate_market_insights_btn"):
            with st.spinner("AI正在分析市场..."):
                try:
                    if st.session_state.analyzer:
                        ai_analysis = st.session_state.analyzer.generate_market_insights(insight_type)
                        if ai_analysis:
                            st.markdown("### 🎯 市场洞察报告")
                            st.markdown(ai_analysis)
                        else:
                            st.error("市场洞察生成失败")
                    else:
                        st.error("分析器未初始化")
                except Exception as e:
                    st.error(f"市场洞察分析失败: {str(e)}")
    
    def _parse_fundamental_analysis(self, analysis_text: str) -> Dict[str, str]:
        """
        解析基本面分析文本，分割成不同的部分
        
        Args:
            analysis_text: AI生成的基本面分析文本
            
        Returns:
            分割后的分析部分字典
        """
        sections = {}
        
        # 尝试按常见的标题分割
        common_headers = [
            "财务健康度分析", "估值分析", "盈利能力分析", "成长性分析", 
            "行业对比分析", "风险评估", "投资建议", "总结"
        ]
        
        current_section = "概述"
        current_content = []
        
        lines = analysis_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 检查是否是新的章节标题
            is_header = False
            for header in common_headers:
                if header in line or any(keyword in line for keyword in ["##", "**", "###"]):
                    if current_content:
                        sections[current_section] = '\n'.join(current_content)
                        current_content = []
                    current_section = line.replace('#', '').replace('*', '').strip()
                    is_header = True
                    break
            
            if not is_header:
                current_content.append(line)
        
        # 添加最后一个部分
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        # 如果没有找到标题，直接返回原文
        if len(sections) <= 1:
            sections = {"基本面分析": analysis_text}
        
        return sections
    
    def _save_analysis_to_history(self, stock_name: str):
        """保存分析到历史记录"""
        if 'current_single_stock_analysis' in st.session_state:
            analysis = st.session_state.current_single_stock_analysis
            
            if stock_name not in st.session_state.single_stock_analysis_history:
                st.session_state.single_stock_analysis_history[stock_name] = []
            
            # 添加到历史记录
            st.session_state.single_stock_analysis_history[stock_name].append(
                (analysis['timestamp'], analysis)
            )
            
            # 保持最多10条历史记录
            if len(st.session_state.single_stock_analysis_history[stock_name]) > 10:
                st.session_state.single_stock_analysis_history[stock_name] = \
                    st.session_state.single_stock_analysis_history[stock_name][-10:]
    
    def _parse_single_stock_analysis(self, analysis_text: str) -> Dict[str, str]:
        """
        解析单股分析文本，分割成不同的部分
        
        Args:
            analysis_text: AI生成的单股分析文本
            
        Returns:
            分割后的分析部分字典
        """
        sections = {}
        
        # 尝试按常见的标题分割
        common_headers = [
            "股票概况", "技术分析", "成交量分析", "风险评估", "投资建议",
            "基本面分析", "市场情绪", "竞争对手分析", "总结", "操作建议"
        ]
        
        current_section = "概述"
        current_content = []
        
        lines = analysis_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 检查是否是新的章节标题
            is_header = False
            for header in common_headers:
                if header in line or any(keyword in line for keyword in ["##", "**", "###", "1.", "2.", "3.", "4.", "5."]):
                    if current_content:
                        sections[current_section] = '\n'.join(current_content)
                        current_content = []
                    current_section = line.replace('#', '').replace('*', '').replace('1.', '').replace('2.', '').replace('3.', '').replace('4.', '').replace('5.', '').strip()
                    is_header = True
                    break
            
            if not is_header:
                current_content.append(line)
        
        # 添加最后一个部分
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        # 如果没有找到标题，直接返回原文
        if len(sections) <= 1:
            sections = {"单股分析": analysis_text}
        
        return sections
    
    def _export_analysis_report(self, stock_name: str, analysis_content: str):
        """导出分析报告"""
        try:
            # 创建报告内容
            report_content = f"""
# {stock_name} AI分析报告

**生成时间**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
**分析工具**: Ashare AI Strategy Analyst

---

{analysis_content}

---

*本报告由AI生成，仅供参考，不构成投资建议。投资有风险，入市需谨慎。*
            """
            
            # 提供下载
            st.download_button(
                label="📥 下载分析报告",
                data=report_content,
                file_name=f"{stock_name}_AI分析报告_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                key="download_report_btn"
            )
            
        except Exception as e:
            st.error(f"导出报告失败: {str(e)}") 