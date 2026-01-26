"""
配置页面模块
"""

import streamlit as st
import pandas as pd
import re
import requests
from datetime import datetime
from typing import Dict, List, Optional

from ashare.analyzer import StockAnalyzer
from ashare.search import stock_searcher


class ConfigPage:
    """配置页面组件"""
    
    def __init__(self, config):
        """初始化配置页面"""
        self.config = config
    
    def render(self):
        """渲染配置页面"""
        # 现代化页面标题
        st.markdown("""
        <div class="fade-in" style="text-align: center; padding: 1rem 0 2rem 0;">
            <h1 style="font-size: 2.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;">
                ⚙️ 智能配置
            </h1>
            <p style="color: #6c757d; font-size: 1.1rem;">
                个性化配置您的股票分析参数
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 初始化股票池状态
        if 'current_stock_pool' not in st.session_state:
            st.session_state.current_stock_pool = {}
        
        # 股票池配置
        st.markdown("### 📋 股票池配置")
        
        # 股票搜索和添加功能
        st.markdown("#### 🔍 智能股票搜索")
        
        search_col1, search_col2 = st.columns([3, 1])
        
        with search_col1:
            search_query = st.text_input(
                "搜索股票（输入股票名称、代码或关键词）",
                placeholder="例如：招商银行、sh600036、腾讯控股、新能源、医药",
                help="支持股票名称、代码、行业关键词搜索",
                key="stock_search_input"
            )
            
            # 实时搜索建议
            if search_query and len(search_query) >= 2:
                suggestions = stock_searcher.suggest_keywords(search_query)
                if suggestions:
                    st.markdown("💡 **搜索建议：**")
                    suggestion_text = " | ".join([f"`{s}`" for s in suggestions[:5]])
                    st.markdown(f"<small>{suggestion_text}</small>", unsafe_allow_html=True)
        
        with search_col2:
            if st.button("🔍 搜索", type="primary", key="search_button"):
                if search_query.strip():
                    self.search_and_add_stock(search_query.strip())
        
        # 显示搜索结果
        if 'search_results' in st.session_state and st.session_state.search_results:
            st.markdown("#### 📊 搜索结果")
            
            for i, result in enumerate(st.session_state.search_results):
                col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
                
                with col1:
                    st.markdown(f"**{result['name']}** ({result['code']})")
                
                with col2:
                    st.markdown(f"*{result['market']}*")
                
                with col3:
                    if 'category' in result and result['category']:
                        st.markdown(f"🏷️ {result['category']}")
                
                with col4:
                    # 显示匹配类型和分数
                    match_type = result.get('match_type', 'unknown')
                    score = result.get('score', 0)
                    if score > 0:
                        st.markdown(f"⭐ {score}")
                
                with col5:
                    if st.button(f"➕ 添加", key=f"add_{i}"):
                        st.session_state.current_stock_pool[result['name']] = result['code']
                        st.success(f"✅ 已添加 {result['name']} 到股票池")
                        st.rerun()
            
            st.markdown("---")
        
        # 预设股票池选择
        st.markdown("#### 📋 预设股票池")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 预设股票池
            preset_options = {
                "项目股票池": {
                    "北方稀土": "sh600111",
                },
                "热门指数": {
                    "上证指数": "sh000001",
                    "深证成指": "sz399001", 
                    "创业板指": "sz399006",
                    "科创50": "sh000688",
                    "沪深300": "sh000300",
                    "中证500": "sh000905"
                },
                "热门个股": {
                    "招商银行": "sh600036",
                    "平安银行": "sz000001",
                    "贵州茅台": "sh600519",
                    "腾讯控股": "00700.HK",
                    "中国平安": "sh601318",
                    "比亚迪": "sz002594",
                    "宁德时代": "sz300750"
                },
                "清空股票池": {}
            }
            
            selected_preset = st.selectbox(
                "选择预设股票池",
                list(preset_options.keys()),
                index=0,
                help="选择预设股票池或清空当前股票池",
                key="preset_selectbox"
            )
            
            if selected_preset == "清空股票池":
                if st.button("🗑️ 清空当前股票池", key="clear_pool_button"):
                    st.session_state.current_stock_pool = {}
                    st.success("✅ 股票池已清空")
                    st.rerun()
            else:
                if st.button("📥 加载预设股票池", key="load_preset_button"):
                    st.session_state.current_stock_pool = preset_options[selected_preset].copy()
                    st.success(f"✅ 已加载 {selected_preset}")
                    st.rerun()
            
            # 手动输入股票代码
            st.markdown("#### ✏️ 手动添加股票")
            manual_input = st.text_area(
                "手动输入股票代码（格式：代码 名称，每行一个）",
                placeholder="sh000001 上证指数\nsz399001 深证成指\nsh600036 招商银行",
                height=100,
                help="格式：股票代码 股票名称",
                key="manual_input_textarea"
            )
            
            if st.button("➕ 添加手动输入的股票", key="add_manual_button"):
                if manual_input.strip():
                    self.add_manual_stocks(manual_input.strip())
            
        with col2:
            st.markdown("#### 📊 分析参数")
            
            data_count = st.slider(
                "历史数据天数",
                min_value=60,
                max_value=500,
                value=120,
                step=20,
                help="获取用于分析的历史交易日数据量",
                key="data_count_slider"
            )
            
            enable_ai = st.checkbox(
                "启用AI分析",
                value=bool(self.config.llm_api_key),
                help="需要配置LLM API密钥",
                disabled=not bool(self.config.llm_api_key),
                key="enable_ai_checkbox"
            )
            
            enable_multi_timeframe = st.checkbox(
                "多时间框架分析",
                value=True,
                help="同时分析日线、周线、月线数据",
                key="enable_multi_timeframe_checkbox"
            )
        
        # 显示当前股票池
        if st.session_state.current_stock_pool:
            st.markdown("### 📈 当前股票池")
            
            # 股票池管理
            pool_col1, pool_col2 = st.columns([3, 1])
            
            with pool_col1:
                pool_df = pd.DataFrame([
                    {"股票名称": name, "股票代码": code}
                    for name, code in st.session_state.current_stock_pool.items()
                ])
                st.dataframe(pool_df, use_container_width=True, hide_index=True)
            
            with pool_col2:
                st.markdown("#### 🗑️ 管理股票池")
                
                # 选择要删除的股票
                if st.session_state.current_stock_pool:
                    stock_to_remove = st.selectbox(
                        "选择要删除的股票",
                        list(st.session_state.current_stock_pool.keys()),
                        key="remove_stock_selectbox"
                    )
                    
                    if st.button("❌ 删除选中股票", key="remove_stock_button"):
                        del st.session_state.current_stock_pool[stock_to_remove]
                        st.success(f"✅ 已删除 {stock_to_remove}")
                        st.rerun()
            
            # 创建分析器按钮
            st.markdown("### 🚀 创建分析器")
            
            if st.button("🔧 创建股票分析器", type="primary", key="create_analyzer_button"):
                if not st.session_state.current_stock_pool:
                    st.error("❌ 请先添加股票到股票池")
                    return
                
                # 创建分析器
                with st.spinner("正在初始化分析器..."):
                    try:
                        st.session_state.analyzer = StockAnalyzer(
                            stock_info=st.session_state.current_stock_pool,
                            count=data_count,
                            config=self.config
                        )
                        
                        st.success("✅ 分析器创建成功！")
                        
                        # 自动跳转到分析页面
                        st.session_state.page = "📊 分析"
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ 创建分析器失败: {str(e)}")
    
    def search_and_add_stock(self, query: str):
        """使用智能搜索器搜索股票"""
        try:
            # 使用智能搜索器
            results = stock_searcher.search_stocks(query, max_results=10)
            
            if results:
                # 转换结果格式以兼容现有代码
                formatted_results = []
                for result in results:
                    formatted_result = {
                        'name': result['name'],
                        'code': result['code'],
                        'market': result['market'],
                        'category': result.get('category', ''),
                        'match_type': result.get('match_type', ''),
                        'score': result.get('score', 0),
                        'is_unknown': result.get('is_unknown', False)
                    }
                    formatted_results.append(formatted_result)
                
                st.session_state.search_results = formatted_results
                st.success(f"🔍 找到 {len(formatted_results)} 个匹配结果")
                
                # 如果有未知股票，显示提示
                unknown_stocks = [r for r in formatted_results if r.get('is_unknown', False)]
                if unknown_stocks:
                    st.info("💡 提示：对于未知股票，您可以手动添加并验证其有效性")
            else:
                st.warning("❌ 未找到匹配的股票")
                st.info("💡 您可以：\n1. 尝试其他关键词\n2. 使用手动输入功能\n3. 检查股票代码格式")
                
        except Exception as e:
            st.error(f"搜索失败: {str(e)}")
    
    def add_manual_stocks(self, manual_input: str):
        """添加手动输入的股票"""
        try:
            added_count = 0
            for line in manual_input.strip().split('\n'):
                if line.strip():
                    parts = line.strip().split(' ')
                    if len(parts) >= 2:
                        code = parts[0]
                        name = ' '.join(parts[1:])
                        
                        # 验证股票代码格式
                        if self.is_valid_stock_code(code):
                            st.session_state.current_stock_pool[name] = code
                            added_count += 1
                        else:
                            st.warning(f"⚠️ 股票代码格式无效: {code}")
            
            if added_count > 0:
                st.success(f"✅ 成功添加 {added_count} 只股票到股票池")
                st.rerun()
            else:
                st.error("❌ 没有成功添加任何股票")
                
        except Exception as e:
            st.error(f"添加股票失败: {str(e)}")
    
    def is_valid_stock_code(self, code: str) -> bool:
        """验证股票代码格式"""
        # A股代码格式
        if code.startswith(('sh', 'sz')):
            if len(code) == 8:  # sh600036, sz000001
                return True
            elif len(code) == 9:  # sh000001 (指数)
                return True
        
        # 港股代码格式
        if code.endswith('.HK') and len(code) == 8:  # 00700.HK
            return True
        
        return False 