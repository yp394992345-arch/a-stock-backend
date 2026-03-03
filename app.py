from flask import Flask, jsonify, request
from flask_cors import CORS
import akshare as ak
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route('/api/index', methods=['GET'])
def get_index():
    try:
        df = ak.stock_zh_index_spot()
        indices = df[df['代码'].isin(['000001', '399001', '399006'])]
        result = {}
        for _, row in indices.iterrows():
            code = row['代码']
            result[code] = {
                'name': row['名称'],
                'current': float(row['最新价']) if pd.notna(row['最新价']) else 0,
                'change': float(row['涨跌幅']) if pd.notna(row['涨跌幅']) else 0,
                'volume': float(row['成交量']) if pd.notna(row['成交量']) else 0,
            }
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/market', methods=['GET'])
def get_market_stats():
    try:
        df_limit_up = ak.stock_zh_a_limit_up_spot()
        df_limit_down = ak.stock_zh_a_limit_down_spot()
        df = ak.stock_zh_index_spot()
        advancers = len(df[df['涨跌幅'] > 0])
        decliners = len(df[df['涨跌幅'] < 0])
        return jsonify({
            'advancers': int(advancers),
            'decliners': int(decliners),
            'limitUps': int(len(df_limit_up)) if df_limit_up is not None else 0,
            'limitDowns': int(len(df_limit_down)) if df_limit_down is not None else 0,
        })
    except Exception as e:
        return jsonify({'advancers': 0, 'decliners': 0, 'limitUps': 0, 'limitDowns': 0}), 200

@app.route('/api/sector', methods=['GET'])
def get_sector():
    try:
        df = ak.stock_board_industry_name_em()
        df_sorted = df.sort_values('涨跌幅', ascending=False).head(15)
        result = []
        for _, row in df_sorted.iterrows():
            result.append({
                'code': row['板块代码'],
                'name': row['板块名称'],
                'change': float(row['涨跌幅']) if pd.notna(row['涨跌幅']) else 0,
                'volume': float(row['总市值']) if pd.notna(row['总市值']) else 0,
                'inflow': 0,
            })
        return jsonify(result)
    except Exception as e:
        return jsonify([])

@app.route('/api/limitup', methods=['GET'])
def get_limitup():
    try:
        df = ak.stock_zh_a_limit_up_spot()
        if df is None or df.empty:
            return jsonify([])
        df_limited = df.head(20)
        result = []
        for _, row in df_limited.iterrows():
            result.append({
                'code': row['代码'],
                'name': row['名称'],
                'price': float(row['最新价']) if pd.notna(row['最新价']) else 0,
                'change': float(row['涨跌幅']) if pd.notna(row['涨跌幅']) else 0,
                'reason': row.get('所属行业', '热门') if pd.notna(row.get('所属行业')) else '热门',
            })
        return jsonify(result)
    except Exception as e:
        return jsonify([])

@app.route('/api/kline', methods=['GET'])
def get_kline():
    code = request.args.get('code', 'sh000001')
    try:
        symbol = code.replace('sh', '').replace('sz', '')
        df = ak.stock_zh_index_daily(symbol=symbol)
        if df is None or df.empty:
            return jsonify([])
        df_limited = df.tail(60)
        result = []
        for _, row in df_limited.iterrows():
            result.append({
                'date': str(row['date']),
                'open': float(row['open']) if pd.notna(row['open']) else 0,
                'close': float(row['close']) if pd.notna(row['close']) else 0,
                'high': float(row['high']) if pd.notna(row['high']) else 0,
                'low': float(row['low']) if pd.notna(row['low']) else 0,
                'volume': float(row['volume']) if pd.notna(row['volume']) else 0,
            })
        return jsonify(result)
    except Exception as e:
        return jsonify([])

@app.route('/api/northbound', methods=['GET'])
def get_northbound():
    return jsonify([
        {'time': '09:30', 'inflow': 0},
        {'time': '10:00', 'inflow': 0},
        {'time': '11:30', 'inflow': 0},
        {'time': '14:30', 'inflow': 0},
        {'time': '15:00', 'inflow': 0},
    ])

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
