# 🎬 YouTube Shorts Pipeline

A streamlined pipeline that automatically creates YouTube Shorts with AI-generated facts and subtitles.

## 🚀 What This Does

1. **Generates** engaging fact-based scripts using Gemini AI
2. **Creates** natural speech audio using Edge-TTS
3. **Produces** 9:16 videos with vibrant animated subtitles
4. **Outputs** ready-to-upload YouTube Shorts

## 📁 Project Structure

```
youtube-pipeline/
├── pipeline.py              # Main script - run this!
├── config.json             # Configuration file
├── requirements.txt        # Python dependencies
├── .env                    # Your API keys (create this)
├── input_videos/           # PUT YOUR VIDEOS HERE! 
│   ├── background.mp4      # Your background videos
│   ├── gameplay.mp4        
│   └── nature.mov
├── utils/
│   ├── __init__.py
│   ├── config.py
│   ├── script_generator.py
│   └── video_creator.py
└── output_videos/          # Generated videos appear here
    └── space_facts_20241201_143022.mp4
```

## 🛠️ Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key

### 3. Create .env File
Create a `.env` file in the project root:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Add Your Videos to Input Folder
- Create `input_videos/` folder
- Drop ALL your background videos there:
  - `gameplay.mp4`
  - `nature_scenes.mov` 
  - `abstract_visuals.avi`
  - `cooking_footage.mkv`
  - etc.
- Any video format works (MP4, MOV, AVI, MKV, WMV)

### 5. Configure Settings
Edit `config.json`:
```json
{
  "input_folder": "input_videos",           // Your video folder
  "output_folder": "output_videos",         // Where finals go
  "background_video_name": "random",        // "random" or "specific.mp4"
  "topic": null,                           // null = random topic
  "subtitle_style": "ultra_vibrant"        // Style choice
}
```

## 🎯 Usage Options

### Option 1: Random Everything (Easiest)
```bash
python pipeline.py
```
- Picks random video from your input folder
- Generates random engaging fact
- Creates video automatically

### Option 2: Specific Video
In `config.json`:
```json
{
  "background_video_name": "gameplay.mp4"  // Use specific video
}
```

### Option 3: Specific Topic
In `config.json`:
```json
{
  "topic": "Space and Astronomy"  // Focus on specific topic
}
```

## 📂 How Input/Output Works

**Input Folder** (`input_videos/`):
- Put ALL your background videos here
- Any format: `.mp4`, `.mov`, `.avi`, `.mkv`, `.wmv`
- Any resolution (auto-cropped to 9:16)
- Set to `"random"` to pick randomly each run

**Output Folder** (`output_videos/`):
- Final videos saved as: `{topic}_{timestamp}.mp4`
- Example: `space_facts_20241201_143022.mp4`
- Ready to upload to YouTube

## 📋 Available Topics

- Space and Astronomy
- Ocean and Marine Life
- Human Body
- Ancient History
- Technology
- Animals
- Food and Nutrition
- Psychology
- Geography
- Science Discoveries
- Art and Culture
- Sports
- Music
- Weather and Climate
- Inventions
- Amazing Nature Facts
- Mind-Blowing Physics
- Historical Mysteries
- Future Technology
- Bizarre World Records

## 🎨 Subtitle Styles

- **ultra_vibrant**: Bright yellow text with black outline
- **neon_pop**: Cyan text with magenta outline  
- **fire_text**: Orange-red text with white outline

## 🔊 Available Voices

- `en-US-AriaNeural` - US Female (Natural and friendly)
- `en-US-GuyNeural` - US Male (Professional and clear)
- `en-US-JennyNeural` - US Female (Warm and conversational)
- `en-GB-SoniaNeural` - British Female (Elegant and clear)
- `en-AU-NatashaNeural` - Australian Female (Friendly)

## 📝 Example Workflow

1. **Drop videos** into `input_videos/`:
   ```
   input_videos/
   ├── minecraft_gameplay.mp4
   ├── ocean_footage.mov
   └── space_visuals.avi
   ```

2. **Run pipeline**:
   ```bash
   python pipeline.py
   ```

3. **Get result** in `output_videos/`:
   ```
   output_videos/
   └── ocean_marine_life_20241201_143022.mp4
   ```

## 🔄 Mass Production

Create multiple videos quickly:
```bash
# Each run = new unique video
python pipeline.py  # Creates video 1
python pipeline.py  # Creates video 2  
python pipeline.py  # Creates video 3
```

Each uses different random combinations of:
- Background video (if set to "random")
- Topic/fact content
- Timestamps ensure unique filenames

## 🐛 Troubleshooting

**"No video files found in input_videos"**
- Make sure you created the `input_videos/` folder
- Add video files to it (.mp4, .mov, .avi, etc.)

**"GEMINI_API_KEY not found"**
- Create `.env` file with your API key
- Make sure the key is valid

**"Video not found: specific.mp4"**
- Check the video name in `config.json`
- Make sure the file exists in `input_videos/`

## 🎯 Pro Tips

1. **Multiple Videos**: Keep various background videos for variety
2. **Random Mode**: Set `"background_video_name": "random"` for surprises  
3. **Batch Creation**: Run multiple times for content series
4. **Topic Focus**: Set specific topics for niche content
5. **Quality**: Use high-quality, engaging background footage

---

🎉 **Just drop videos in input folder and run! No complicated paths!** 🎉