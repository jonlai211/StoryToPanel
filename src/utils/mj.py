import certifi
import http.client
import json
import logging
import os
import ssl
import time

from dotenv import load_dotenv

load_dotenv()

# Obtain a logger for this module
logger = logging.getLogger(__name__)

API_KEY = os.getenv("MJ_KEY")
HOST_NAME = os.getenv("MJ_HOSTNAME")

HEADERS = {
    'Authorization': f'Bearer {API_KEY}',
    'User-Agent': 'MyPythonApp/1.0',
    'Content-Type': 'application/json'
}


def get_connection():
    context = ssl.create_default_context(cafile=certifi.where())
    return http.client.HTTPSConnection(HOST_NAME, context=context)


def imagine(prompt):
    payload = json.dumps({"prompt": prompt})
    conn = get_connection()
    try:
        conn.request("POST", "/mj/submit/imagine", payload, HEADERS)
        response = conn.getresponse()
        response_data = response.read().decode("utf-8")
        response_json = json.loads(response_data)
        result = response_json.get("result")
        code = response_json.get("code")
        logger.info(f"Imagine Code: {code}, Imagine Result: {result}")
        return result
    except Exception as e:
        logger.error(f"Imagine function error: {e}")
        return None
    finally:
        conn.close()


def fetch(task_id):
    path = f"/mj/task/{task_id}/fetch"
    payload = json.dumps({})
    conn = get_connection()
    try:
        while True:
            time.sleep(5)
            conn.request("GET", path, payload, headers=HEADERS)
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            json_data = json.loads(data)
            url = json_data.get("imageUrl")
            status = json_data.get("status")
            progress = json_data.get("progress")
            buttons = json_data.get("buttons")
            logger.info(f"Fetch Progress: {progress}, Status: {status}")
            if status == "SUCCESS" and url:
                logger.info(f"Successful fetch with URL: {url}, Buttons info: {buttons}")
                return url
            elif status == "FAILURE":
                logger.error(f"Fetch failed for task ID {task_id} with data: {data}")
                return ""
    except Exception as e:
        logger.error(f"Fetch function error: {e}")
    finally:
        conn.close()


def action(customId, taskId):
    payload = json.dumps({
        "customId": customId,
        "taskId": taskId
    })

    conn = get_connection()
    try:
        conn.request("POST", "/mj/submit/action", payload, HEADERS)
        response = conn.getresponse()
        response_data = response.read().decode("utf-8")
        if response.status == 200:
            response_json = json.loads(response_data)
            result = response_json.get("result")
            code = response_json.get("code")
            logger.info(f"Action Code: {code}, Action Result: {result}")
            return result
        else:
            logger.error(f"HTTP Error: Status {response.status}, Response: {response_data}")
            return None
    except Exception as e:
        logger.error(f"Action function error: {e}")
        return None
    finally:
        conn.close()


if __name__ == "__main__":
    identifier = 1

    if identifier == 1:
        prompt = """
Medium shot, front view of a young female protagonist, elegantly dressed in light nightclothes with delicate patterned embroidery on the collar and cuffs. She is notably beautiful, her expression tinged with sadness and helplessness as she looks at luxurious clothes discarded on the ground by palace maids. Her long black hair is styled with a phoenix hairpin. The scene unfolds in an Imperial Garden featuring rock gardens, flowing water, and a profusion of flowers, with several pieces of gorgeous palace attire scattered around. Render this scene in the style of Chinese anime. --niji 6 --no text, watermarks, black bars, border, canvas, matte, frame --sref https://wawawriter-public.oss-cn-hangzhou.aliyuncs.com/dev/1721116784376066.png https://wawawriter-public.oss-cn-hangzhou.aliyuncs.com/dev/1721117219326289.png --sw 100 --ar 16:9 --v 6
        """
        result = imagine(prompt)
        image_url = fetch(result)
        print(image_url)
    elif identifier == 2:
        fetch(1721713840733914)
    elif identifier == 3:
        result = action(customId="MJ::JOB::upsample::1::ed16f97e-1c22-408a-bc63-ff115a0bbb06",
                        taskId="1721617898885100")
        fetch(result)
