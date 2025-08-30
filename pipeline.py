#!/usr/bin/env python3
"""
Streamlined YouTube Shorts Creation Pipeline
Generates fact script -> TTS audio -> Creates video with subtitles
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from pathlib import Path

# Import pipeline modules
from utils.config import Config
from utils.script_generator import ScriptGenerator
from utils.video_creator import VideoCreator

class YouTubePipeline:
    def __init__(self, config_file="config.json"):
        """Initialize the pipeline"""
        self.config = self.load_config(config_file)
        self.setup_directories()
        
        print("🚀 YouTube Shorts Pipeline Starting...")
        print(f"📁 Input Folder: {self.config['input_folder']}")
        print(f"📁 Output Folder: {self.config['output_folder']}")
        print("-" * 60)
    
    def load_config(self, config_file):
        """Load pipeline configuration"""
        default_config = {
            "input_folder": "input_videos",
            "output_folder": "output_videos", 
            "background_video_name": "background.mp4",  # or "random" to pick randomly
            "topic": None,  # None for random topic
            "subtitle_style": "ultra_vibrant",
            "voice": "en-US-AriaNeural",
            "gemini_api_key": os.getenv('GEMINI_API_KEY')
        }
        
        # Try to load config file
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    # Filter out comments
                    user_config = {k: v for k, v in user_config.items() if not k.startswith('_')}
                default_config.update(user_config)
            except:
                print(f"⚠️ Could not load {config_file}, using defaults")
        
        return default_config
    
    def setup_directories(self):
        """Create necessary directories"""
        os.makedirs(self.config['input_folder'], exist_ok=True)
        os.makedirs(self.config['output_folder'], exist_ok=True)
        print(f"📁 Input folder: {self.config['input_folder']}")
        print(f"📁 Output folder: {self.config['output_folder']}")
    
    def get_background_video_path(self):
        """Get the background video to use"""
        input_folder = self.config['input_folder']
        video_name = self.config['background_video_name']
        
        if video_name.lower() == "random":
            # Pick random video from input folder
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
            video_files = []
            for ext in video_extensions:
                video_files.extend(Path(input_folder).glob(f"*{ext}"))
            
            if not video_files:
                raise FileNotFoundError(f"❌ No video files found in {input_folder}")
            
            import random
            selected_video = random.choice(video_files)
            print(f"🎲 Randomly selected: {selected_video.name}")
            return str(selected_video)
        else:
            # Use specific video
            video_path = os.path.join(input_folder, video_name)
            if not os.path.exists(video_path):
                # Try to find it with different extensions
                video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
                base_name = os.path.splitext(video_name)[0]
                for ext in video_extensions:
                    test_path = os.path.join(input_folder, f"{base_name}{ext}")
                    if os.path.exists(test_path):
                        return test_path
                
                raise FileNotFoundError(f"❌ Video not found: {video_path}")
            return video_path
    
    def validate_inputs(self):
        """Validate required inputs exist"""
        if not self.config['gemini_api_key']:
            raise ValueError("❌ GEMINI_API_KEY not found. Set it as environment variable or in config.json")
        
        # Get the video path
        background_video_path = self.get_background_video_path()
        print(f"🎬 Using background video: {background_video_path}")
        
        print("✅ All inputs validated successfully")
        return background_video_path
    
    async def run_pipeline(self):
        """Run the complete pipeline"""
        try:
            # Step 1: Validate inputs
            print("\n🔍 Step 1: Validating inputs...")
            background_video_path = self.validate_inputs()
            
            # Step 2: Generate script
            print("\n📝 Step 2: Generating YouTube script...")
            script_generator = ScriptGenerator(
                api_key=self.config['gemini_api_key']
            )
            
            script_data = script_generator.generate_script(self.config['topic'])
            
            print(f"📺 Topic: {script_data['topic']}")
            print(f"🎯 Hook: {script_data['hook']}")
            print(f"💡 Fact: {script_data['fact']}")
            print(f"📖 Explanation: {script_data['explanation']}")
            print(f"👍 CTA: {script_data['cta']}")
            print(f"⏱️ Estimated Duration: {script_data['estimated_duration']}")
            
            # Step 3: Generate TTS audio
            print("\n🎤 Step 3: Generating speech audio...")
            import edge_tts
            
            full_script = script_data['full_script']
            temp_audio_path = os.path.join(self.config['output_folder'], "temp_speech.mp3")
            
            communicate = edge_tts.Communicate(
                text=full_script,
                voice=self.config['voice']
            )
            
            await communicate.save(temp_audio_path)
            print(f"✅ Audio generated: {temp_audio_path}")
            
            # Step 4: Create video with subtitles
            print("\n🎬 Step 4: Creating video with subtitles...")
            video_creator = VideoCreator()
            
            final_video_path = os.path.join(
                self.config['output_folder'], 
                f"{script_data['topic'].lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            )
            
            success = video_creator.create_youtube_short(
                background_video_path=background_video_path,
                speech_audio_path=temp_audio_path,
                output_path=final_video_path,
                subtitle_style=self.config['subtitle_style']
            )
            
            if success:
                print(f"\n🎉 SUCCESS! YouTube Short created!")
                print(f"📁 Final Video: {final_video_path}")
                print(f"📊 Video Info:")
                print(f"   📺 Topic: {script_data['topic']}")
                print(f"   📝 Words: {script_data['word_count']}")
                print(f"   ⏱️ Duration: ~{script_data['estimated_duration']}")
                print(f"   🎨 Style: {self.config['subtitle_style']}")
                
                # Cleanup temp audio
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
                    print(f"🧹 Cleaned up temporary files")
                
                return final_video_path
            else:
                raise Exception("Video creation failed")
                
        except Exception as e:
            print(f"\n❌ Pipeline failed: {str(e)}")
            return None

def main():
    """Main entry point"""
    print("🎬 YouTube Shorts Creation Pipeline")
    print("=" * 50)
    
    try:
        pipeline = YouTubePipeline()
        result = asyncio.run(pipeline.run_pipeline())
        
        if result:
            print(f"\n🏆 Pipeline completed successfully!")
            print(f"🎥 Your YouTube Short is ready: {result}")
        else:
            print("\n💥 Pipeline failed. Check errors above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Pipeline stopped by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()