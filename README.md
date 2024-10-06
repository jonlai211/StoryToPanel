# StoryToPanel
A tool to convert stories into visual comics panels by generating personas, fragments, plays, and corresponding images.  

## Features  
- **Persona Generation**: Extracts characters (personas) from the story and defines their appearance attributes.  
- **Fragmentation**: Breaks down the story into manageable fragments for narrators lines.  
- **Play Generation**: Creates plays (scenes) from fragments and personas.  
- **Image Generation**: Produces images for each play using AI image generation models.  

## Directory
```  
StoryToPanel/  
├── src/  
│   ├── __init__.py  
│   ├── main.py  
│   ├── generator/  
│   │   ├── __init__.py  
│   │   ├── story_2_persona.py  
│   │   ├── story_2_frag.py  
│   │   ├── frag_2_play.py  
│   │   └── play_2_image.py  
│   ├── utils/  
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   ├── mj.py
│   │   ├── download.py
│   │   ├── style.py
│   │   ├── logger.py  
│   │   ├── utils.py
│   │   └── replace.json
│   └── data/  
│       ├── image/  
│       ├── processed/
│       └── output/  
│           └── results.json  
├── README.md
├── requirements.txt  
└── .venv/ (if using)  
```

## Command-Line Arguments
- `--import_story`: Import story content from a text file.  
	- `--story_file`: Path to the story text file (default: `src/data/processed/ch1-4.txt`).  
- `--generate_personas`: Generate personas from story content.  
- `--generate_fragments`: Generate fragments from story content.  
- `--generate_plays`: Generate plays from fragments and personas.  
- `--generate_images`: Generate images from personas and plays.  
	- `--style`: Style to use for image generation (default: `"国风动漫"`).  
	- `--ratio`: Aspect ratio for image generation (default: `"16:9"`).  
	- `--limit`: Limit the number of plays to process for image generation.  
- `--output_file`: Path to the output JSON file (default: `src/data/output/results.json`).  

## Env Setup
### `.env` File
Create a `.env` file in the root directory with the following environment variables.  
```plaintext
TEXT_MODEL="model name"
TEXT_MODEL_KEY="sk-..."
TEXT_MODEL_URL="https://HOSTNAME"

MJ_KEY="sk-..."
MJ_HOSTNAME="HOSTNAME"
```

## Example Workflow
Here is an example of how to execute the entire workflow step-by-step.  
#### **1. Import Story**  
```bash  
python -m src.main --import_story --story_file src/data/harry_potter.txt
```  
#### **2. Generate Personas**  
```bash  
python -m src.main --generate_personas
``` 
#### **3. Generate Fragments**  
```bash  
python -m src.main --generate_fragments
```  
#### **4. Generate Plays**  
```bash  
python -m src.main --generate_plays
```
#### **5. Generate Images**  
```bash  
python -m src.main --generate_images --style "Disney" --ratio "16:9" --limit 5
```
#### **6. Run All Steps Together**  
```bash  
python -m src.main --import_story --generate_personas --generate_fragments --generate_plays --generate_images --story_file data/processed/ch1-4.txt --style "国风动漫" --ratio "16:9" --limit 5
```  

## Comic Styles
The styles are set in `src/utils/style.py` and can be modified as needed.
- [ ] Add styles sample images here

## Sample `results.json` Structure
```json
{
	"story_content": "第一章 黑魔王崛起\n\n　　两个男人从虚空中突然现身，在月光映照的窄巷里相隔几米。他们一动不动地站立了...",
    "personas": [
        "Persona(name=斯内普, gender=男, age=中年, appearance=衣着黑色的长袍，像是某种古老的巫师长袍，显得他更加阴沉和神秘。 外观消瘦的面孔，鹰钩鼻，脸色苍白，长长的黑头发油腻腻的，垂在肩上。黑色的眼睛深邃而冷漠，嘴角总是带着一丝嘲讽的弧度。)",
        "Persona(name=亚克斯利, gender=男, age=中年, appearance=衣着黑色的长斗篷，里面是精致的巫师长袍，胸口别着一枚银色的胸针。 外观粗壮的身材，面色红润，头发稀疏，浓密的眉毛下藏着一双精明的眼睛。)",
        "Persona(name=伏地魔, gender=男, age=老年, appearance=衣着黑色的长袍，上面绣着银色的符文，显得神秘而邪恶。 外观没有头发，像蛇一样，两道细长的鼻孔，一双闪闪发亮的红眼睛，瞳孔是垂直的。他的肤色十分苍白，似乎发出一种珍珠般的光。)"
    ],
    "cast": [
        "斯内普",
        "亚克斯利",
        "伏地魔"
    ],
    "fragments": [
        "Fragment 1: 两个男人从虚空中突然现身，在月光映照的窄巷里相隔几米。他们一动不动地站立了一秒钟，用魔杖指着对方的胸口。接着，两人互相认了出来，便把魔杖塞进斗篷下面，朝同一方向快步走去。",
        "Fragment 2: “有消息吗？”个子高一些的那人问。“再好不过了。”西弗勒斯·斯内普回答。",
        "Fragment 3: 小巷左边是胡乱生长的低矮的荆棘丛，右边是修剪得整整齐齐的高高的树篱。两人大步行走，长长的斗篷拍打着他们的脚踝。"
	],
    "plays": [
        {
            "id": "1",
            "play_roles": "斯内普, 亚克斯利",
            "play_roles_actions": "斯内普，突然出现，站立不动，魔杖指着对方，表情警惕。亚克斯利，突然出现，站立不动，魔杖指着对方，表情警惕。",
            "play_environment": "窄巷：月光映照，两侧是建筑物的墙壁，地面铺着不平整的石板",
            "play_distance": "中景",
            "play_direction": "正拍"
        },
        {
            "id": "2",
            "play_roles": "斯内普, 亚克斯利",
            "play_roles_actions": "斯内普，将魔杖塞进斗篷，转头看向对方，表情放松。亚克斯利，将魔杖塞进斗篷，转头看向对方，表情放松。",
            "play_environment": "窄巷：月光映照，两侧是建筑物的墙壁，地面铺着不平整的石板",
            "play_distance": "中景",
            "play_direction": "正拍"
        }
    ],
    "image_urls": [
        "https://xx/image/1728250071309JHE",
        "https://xxx/image/1728250158555FCE"
    ]
}
```

## Sample Comics
- [ ] Add sample comics here

## License
StoryToPanel is licensed under [MIT License](LICENSE).
