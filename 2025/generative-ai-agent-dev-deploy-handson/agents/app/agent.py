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


def get_weather(query: str) -> str:
    """ウェブ検索をシミュレートします。天気に関する情報を取得するために使用します。

    Args:
        query: 天気情報を取得する場所を含む文字列。
                このクエリ文字列は英語である必要があります。
                例: [Tokyo, New York]

    Returns:
        照会された場所のシミュレートされた天気情報を含む文字列。
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "気温は60度で霧がかかっています。"
    return "気温は90度で晴れです。"


root_agent = Agent(
    name="root_agent",
    model="gemini-2.5-flash",
    instruction="あなたは、正確で役立つ情報を提供するために設計された、親切なAIアシスタントです。",
    tools=[get_weather],
)
