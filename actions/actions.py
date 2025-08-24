# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import requests

class ActionGetAllProducts(Action):
    def name(self):
        return "action_get_all_products"

    def run(self, dispatcher, tracker, domain):
        metadata = tracker.latest_message.get("metadata", {})
        token = metadata.get("access_token")

        if not token:
            dispatcher.utter_message(text="Không tìm thấy token từ UI.")
            return []

        headers = {
            "Authorization": f"Bearer {token}"
        }

        try:
            response = requests.get(
                "http://localhost:8083/api/products/",
                headers=headers
            )

            print("Status Code:", response.status_code)
            print("Response Text:", response.text)

            if response.status_code == 200:
                try:
                    products = response.json()
                    dispatcher.utter_message(text=f"Products: {products}")
                except Exception as parse_error:
                    dispatcher.utter_message(text=f"Lỗi khi parse JSON: {parse_error}")
            else:
                dispatcher.utter_message(
                    text=f"Không lấy được sản phẩm. Mã lỗi: {response.status_code}, Nội dung: {response.text}"
                )

        except Exception as e:
            dispatcher.utter_message(text=f"Lỗi gọi API: {e}")

        return []

import requests
from rasa_sdk import Action

class ActionSanPhamBanChay(Action):
    def name(self):
        return "action_san_pham_ban_chay"

    def run(self, dispatcher, tracker, domain):
        # Lấy token từ metadata (gửi từ UI)
        metadata = tracker.latest_message.get("metadata", {})
        token = metadata.get("access_token")

        if not token:
            dispatcher.utter_message(text="Không tìm thấy token từ UI.")
            return []

        headers = {
            "Authorization": f"Bearer {token}"
        }

        try:
            # Lấy statusCode từ slot, mặc định 'DELIVERED'
            status_code = tracker.get_slot("statusCode") or 'DELIVERED'

            # Gọi API
            response = requests.get(
                "http://localhost:8083/api/orders/revenues/status",
                headers=headers,
                params={"statusCode": status_code}
            )

            print("Status Code:", response.status_code)
            print("Response Text:", response.text)

            if response.status_code == 200:
                try:
                    res_json = response.json()
                    best_selling = res_json.get("data", [{}])[0].get("bestSellingProduct", [])

                    if best_selling:
                        sp = best_selling[0]  # Chỉ lấy 1 sản phẩm bán chạy nhất
                        variant = sp.get("productVariant", {})
                        product_id = variant.get("productId", "")
                        price = variant.get("price", 0)
                        # Link tới productId
                        link = f"http://localhost:3000/products/{product_id}"
                        message = f"🔥 Sản phẩm bán chạy nhất hiện nay: [Tại đây]({link}) (Giá: {price} VND)"
                    else:
                        message = "Hiện tại chưa có sản phẩm nào được xếp hạng bán chạy."

                    dispatcher.utter_message(text=message)

                except Exception as parse_error:
                    dispatcher.utter_message(text=f"Lỗi khi parse JSON: {parse_error}")
            else:
                dispatcher.utter_message(
                    text=f"Không lấy được sản phẩm bán chạy. "
                         f"Mã lỗi: {response.status_code}, Nội dung: {response.text}"
                )

        except Exception as e:
            dispatcher.utter_message(text=f"Lỗi gọi API: {e}")

        return []
