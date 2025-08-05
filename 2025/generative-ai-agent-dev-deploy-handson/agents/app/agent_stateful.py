# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import os
from zoneinfo import ZoneInfo

import google.auth
from google.adk.agents import Agent

_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


from google.adk.tools.tool_context import ToolContext

# Session Stateに基づいて天気情報を返す関数
def get_weather_stateful(city: str, tool_context: ToolContext) -> dict:
    """指定された都市の現在の天気予報を取得します、セッションの状態に基づいて温度の単位を変換します。

    Args:
        city (str): 日本語での都市名（例：「ニューヨーク」、「ロンドン」、「東京」）。
        tool_context (ToolContext): ツール呼び出しのコンテキストを提供し、呼び出しコンテキスト、関数呼び出しID、イベントアクション、認証レスポンスへのアクセスを含みます。

    Returns:
        dict: 天気情報を含む辞書。
              'status' キー（'success' または 'error'）を含みます。
              'success' の場合、天気の詳細情報を持つ 'report' キーを含みます。
              'error' の場合、'error_message' キーを含みます。
    """

    print(f"--- ツール: get_weather_stateful が {city} のために呼び出されました ---")

    # --- 状態から設定を読み込み ---
    preferred_unit = tool_context.state.get("user_preference_temperature_unit", "Celsius")
    print(f"--- ツール: 状態 'user_preference_temperature_unit' を読み込み中: {preferred_unit} ---")


    # モックの天気データ（内部では常に摂氏で保存）
    mock_weather_db = {
        "ニューヨーク": {"temp_c": 25, "condition": "晴れ"},
        "ロンドン": {"temp_c": 15, "condition": "曇り"},
        "東京": {"temp_c": 18, "condition": "雨"},
    }

    if city in mock_weather_db:
        data = mock_weather_db[city]
        temp_c = data["temp_c"]
        condition = data["condition"]

        if preferred_unit == "Fahrenheit":
            temp_value = (temp_c * 9/5) + 32
            temp_unit = "°F"
        else:
            temp_value = temp_c
            temp_unit = "°C"

        report = f"{city.capitalize()}の天気は{condition}で、気温は{temp_value:.0f}{temp_unit}です。"
        result = {"status": "success", "report": report}
        print(f"--- ツール: {preferred_unit}でレポートを生成しました。結果: {result} ---")
        return result
    else:
        # 都市が見つからない場合の処理
        error_msg = f"申し訳ありませんが、'{city}'の天気情報はありません。"
        print(f"--- ツール: 都市 '{city}' が見つかりませんでした。 ---")
        return {"status": "error", "error_message": error_msg}

print("✅ 状態認識ツール 'get_weather_stateful' が定義されました。")

# ユーザーの好みを記憶する

def set_temperature_preference(unit: str, tool_context: ToolContext) -> dict:
    """ユーザーの希望する温度単位（摂氏または華氏）を設定します。

    引数:
        unit (str): 希望する温度単位（"Celsius" または "Fahrenheit"）。
        tool_context (ToolContext): セッション状態へのアクセスを提供するADKツールコンテキスト。

    戻り値:
        dict: 処理の確認またはエラーを報告する辞書。
    """
    print(f"--- Tool: set_temperature_preference called with unit: {unit} ---")
    normalized_unit = unit.strip().capitalize()

    if normalized_unit in ["Celsius", "Fahrenheit"]:
        tool_context.state["user_preference_temperature_unit"] = normalized_unit
        print(f"--- Tool: Updated state 'user_preference_temperature_unit': {normalized_unit} ---")
        return {"status": "success", "message": f"Temperature preference set to {normalized_unit}."}
    else:
        error_msg = f"Invalid temperature unit '{unit}'. Please specify 'Celsius' or 'Fahrenheit'."
        print(f"--- Tool: Invalid unit provided: {unit} ---")
        return {"status": "error", "error_message": error_msg}

root_agent = Agent(
        name="weather_agent_stateful", # 新しいバージョン名
        model="gemini-2.5-flash",
        description="メインエージェント: 天気情報を提供し（状態認識ユニット）レポートを状態に保存します。",
        instruction="あなたはメインの天気エージェントです。あなたの仕事は 'get_weather_stateful' を使って天気情報を提供することです。"
                    "このツールは、状態に保存されているユーザーの好みに基づいて温度の形式を設定します。",
        tools=[get_weather_stateful,set_temperature_preference], # 状態認識ツールを使用
        output_key="last_weather_report" # <<< エージェントの最終的な天気応答を自動保存
    )