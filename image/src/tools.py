import json
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import re

REFERENCE_VALUES = [
        1800000, 9000000, 9000000, 2700000, 2700000,
        2790000, 2790000, 2790000, 2790000,
        3600000, 3600000, 3900000, 3600000,
        3600000, 3600000, 3600000, 3600000
    ]

MACHINE_NAMES = [
    "slit cut count", "forming press count", "forming pin hole count",
    "ai sheet cutter count upper", "ai sheet cutter count lower",
    "[front] pouch top cut count upper", "[front] pouch top cut count lower",
    "[rear] pouch top cut count upper", "[rear] pouch top cut count lower",
    "[front] sealer count upper", "[front] sealer count lower",
    "[rear] sealer count upper", "[rear] sealer count lower",
    "[front] 2nd sealer count upper", "[front] 2nd sealer count lower",
    "[rear] 2nd sealer count upper", "[rear] 2nd sealer count lower"
]

load_dotenv()

IS_USING_IMAGE_RUNTIME = None
IS_USING_IMAGE_RUNTIME = os.getenv('IS_USING_IMAGE_RUNTIME', None)

if IS_USING_IMAGE_RUNTIME is not None:
    IMAGE_PATH = '/tmp/images/'
    REPORT_PATH = '/tmp/reports/'
else:
    IMAGE_PATH = 'images/'
    REPORT_PATH = 'reports/'


def list_images_in_folder(folder_path=IMAGE_PATH) -> str:
    print(f"Listing images in folder================== {folder_path}")
    if not os.path.isdir(folder_path):
        return f"Folder does not exist: {folder_path}"

    files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.lower().endswith(('.jpg', '.png'))
    ]

    if not files:
        return "There is no images in the folder."

    return ", ".join(files)


def create_ocr_result(image_path):
    response = requests.post(
        'https://api.ocr.space/parse/image',
        files={'file': open(image_path, 'rb')},
        data={
            'isOverlayRequired': False,
            'OCREngine': 2,
            'istable': True,
            'apikey': os.getenv('OCR_SPACE_API_KEY'),
            'filetype': 'PNG'
        }
    )
    return response.json()


def extract_count_from_ocr_result(data):
    import re

    lines = data["ParsedResults"][0]["TextOverlay"]["Lines"]

    # Find the line name that contains "#"
    line_info = "Unknown"
    for line in lines:
        match = re.search(r"#\s*(\d+\s*-\s*\d+)", line["LineText"])
        if match:
            line_info = match.group(1).strip()
            break


    # Find the line that contains "Count"
    start_index = -1
    for idx, line in enumerate(lines):
        if line["LineText"].strip().lower() == "count":
            start_index = idx + 1
            break

    if start_index == -1:
        print("Can't find 'Count'")
        return None

    # Get the next 17 lines after "Count"
    count_values = []
    for line in lines[start_index:start_index + 17]:
        text = line["LineText"].strip()
        if text.isdigit():
            count_values.append(int(text))

    return {
        "line": line_info,
        "count_values": count_values
    }


def process_multiple_images(image_paths_str: str) -> str:
    image_paths = [p.strip() for p in image_paths_str.split(",") if p.strip()]
    all_results = []

    for image_path in image_paths:
        try:
            ocr_result = create_ocr_result(image_path)
            extracted = extract_count_from_ocr_result(ocr_result)
            if extracted:
                all_results.append(extracted)
        except Exception as e:
            all_results.append({
                "line": f"Error in {image_path}",
                "count_values": [str(e)]
            })

    try:
        json_str = json.dumps(all_results)
        print("[DEBUG] Returning JSON string from process_multiple_images")
        return json_str
    except Exception as e:
        return f"Error creating JSON: {e}"



def compare_count_values_to_reference(results_json: str) -> str:
    try:
        results = json.loads(results_json)
    except Exception as e:
        return f"❌ Error parsing JSON: {e}"
    
    if not isinstance(results, list):
        return "❌ Invalid format: expected a list of line data."

    report = []
    for result in results:
        line = result.get("line", "Unknown")
        counts = result.get("count_values", [])
        report.append(f"Line {line}:")
        for i, (count, ref) in enumerate(zip(counts, REFERENCE_VALUES)):
            name = MACHINE_NAMES[i] if i < len(MACHINE_NAMES) else f"Count {i+1}"
            symbol = "Good: " if count <= ref else "NG: "
            compare_sign = "≤" if count <= ref else ">"
            report.append(f"  {symbol} {name}: {count} {compare_sign} {ref}")
        report.append("")
    print("============= Comparison Generated =============: ", "\n".join(report))
    return "\n".join(report)


def generate_full_report_from_processed_results(processed_results_str: str) -> str:
    comparison_text = compare_count_values_to_reference(processed_results_str)

    today = datetime.now().strftime("%d-%m-%Y")
    full_report = f"INSPECTION REPORT - TODAY: {today}\n" + "-"*60 + "\n\n" + comparison_text

    report_title = f"Inspection Report - {today}"
    save_report_to_txt(full_report, title=report_title)

    return {
        "report_title": report_title,
        "report_content": full_report
    }


def save_report_to_txt(report_text: str, title: str = "Report") -> None:
    filename = f"{title.replace(' ', '_')}.txt"
    folder = REPORT_PATH
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report_text)
        print(f"Report saved to {filepath}")
    except Exception as e:
        print(f"Error saving report: {e}")




if __name__ == "__main__":
    # image_list = [
    #     "images/1.jpg",
    #     "images/2.jpg",
    #     "images/3.jpg"
    # ]
    # process_multiple_images(image_list)

    a = list_images_in_folder("images")
    print("Image list:", a)