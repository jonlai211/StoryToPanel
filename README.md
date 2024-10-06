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
│   │   └── utils.py
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

## Example Workflow
Here is an example of how to execute the entire workflow step-by-step.  
#### **1. Import Story**  
```bash  
python -m src.main --import_story --story_file src/data/processed/ch1.txt
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
python -m src.main --generate_images --style "国风动漫" --ratio "16:9" --limit 5
```
#### **6. Run All Steps Together**  
```bash  
python -m src.main --import_story --generate_personas --generate_fragments --generate_plays --generate_images --story_file data/processed/ch1-4.txt --style "国风动漫" --ratio "16:9" --limit 5
```  

## Comic Styles
```python

```

## Sample `results.json` Structure
```json

```

## Sample Comics

## License
StoryToPanel is licensed under [MIT License]()
