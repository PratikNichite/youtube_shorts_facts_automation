"""
Streamlined Video Creator for YouTube Shorts with Subtitles
"""
import os
import random
import whisper
import textwrap
from typing import Dict, List
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip

class VideoCreator:
    """Creates YouTube Shorts with automatic subtitles"""
    
    def __init__(self):
        self.target_width = 1080
        self.target_height = 1920
        self.whisper_model = None
        
        # Safe text area for vertical centering
        self.text_margin = 80
        self.safe_text_width = self.target_width - (self.text_margin * 2)
        self.max_text_height = 800
        
        # Timing controls to prevent overlap
        self.min_gap_between_text = 0.1
        self.min_display_time = 1.0
        self.max_display_time = 3.0
        
        # Font fallback list (most reliable first)
        self.safe_fonts = [
            None,           # Default system font
            'Arial',        # Windows/Mac
            'DejaVu-Sans',  # Linux
            'Helvetica',    # Mac
            'Liberation-Sans' # Linux fallback
        ]
    
    def create_youtube_short(self, background_video_path: str, speech_audio_path: str,
                           output_path: str, subtitle_style: str = "ultra_vibrant") -> bool:
        """Create YouTube Short with subtitles"""
        try:
            print("🤖 Loading Whisper AI for subtitle generation...")
            if not self.whisper_model:
                self.whisper_model = whisper.load_model("base")
            
            print("🎬 Loading background video...")
            background_video = VideoFileClip(background_video_path)
            
            print("🎵 Loading speech audio...")
            speech_audio = AudioFileClip(speech_audio_path)
            
            print("🧠 Analyzing speech with AI...")
            transcript_result = self.whisper_model.transcribe(
                speech_audio_path,
                word_timestamps=True,
                language="en"
            )
            
            print("📏 Preparing video format (9:16) with random start time...")
            video_duration = speech_audio.duration
            background_resized = self._resize_to_shorts_format_with_random_start(
                background_video, video_duration
            )
            
            # Add speech audio to video
            video_with_audio = background_resized.with_audio(speech_audio)
            
            print("📤 Creating vibrant subtitles...")
            subtitle_clips = self._create_vibrant_subtitles(transcript_result, subtitle_style)
            
            print("🎞️ Compositing final video...")
            final_video = CompositeVideoClip([video_with_audio] + subtitle_clips)
            
            print("💾 Rendering final video...")
            final_video.write_videofile(
                output_path,
                fps=30,
                codec='libx264',
                audio_codec='aac',
                bitrate='8000k',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            print("✅ Video created successfully!")
            
            # Cleanup
            background_video.close()
            speech_audio.close()
            final_video.close()
            
            return True
            
        except Exception as e:
            print(f"❌ Video creation error: {str(e)}")
            return False
    
    def _resize_to_shorts_format_with_random_start(self, video, required_duration):
        """Resize to 9:16 YouTube Shorts format and select random start time"""
        target_aspect = 9/16
        current_aspect = video.w / video.h
        
        # First resize the video to correct aspect ratio
        if current_aspect > target_aspect:
            # Video is too wide, crop width
            new_width = int(video.h * target_aspect)
            x_center = video.w // 2
            x1 = x_center - new_width // 2
            x2 = x_center + new_width // 2
            video_cropped = video.cropped(x1=x1, x2=x2)
            video_resized = video_cropped.resized(height=self.target_height)
        else:
            # Video is correct aspect or too tall
            video_resized = video.resized(height=self.target_height)
        
        # Now handle the timing with random start
        background_duration = video_resized.duration
        
        # Ensure we have enough video duration for the required audio duration
        if background_duration < required_duration:
            print(f"⚠️ Background video ({background_duration:.1f}s) is shorter than audio ({required_duration:.1f}s)")
            print("🔄 Looping background video to match audio duration...")
            return video_resized.loop(duration=required_duration)
        
        # Calculate safe random start time
        # We need at least 'required_duration' seconds remaining after the start time
        max_start_time = background_duration - required_duration
        
        if max_start_time <= 0:
            # This shouldn't happen given our check above, but just in case
            print("🎯 Using video from beginning (no room for random start)")
            random_start = 0
        else:
            # Pick random start time ensuring we have enough duration remaining
            random_start = random.uniform(0, max_start_time)
            print(f"🎲 Random start time: {random_start:.1f}s (video duration: {background_duration:.1f}s)")
        
        # Extract the portion we need starting from random_start
        end_time = random_start + required_duration
        return video_resized.subclipped(random_start, end_time)
    
    def _create_vibrant_subtitles(self, transcript_result, style="ultra_vibrant"):
        """Create vibrant subtitles with font safety"""
        subtitle_clips = []
        
        # Vibrant styles
        styles = {
            "ultra_vibrant": {
                "font_size": 75,
                "color": "#FFFF00",        # Bright yellow
                "stroke_color": "#000000", # Black outline
                "stroke_width": 8,
                "max_chars_per_line": 28
            },
            "neon_pop": {
                "font_size": 78,
                "color": "#00FFFF",        # Cyan
                "stroke_color": "#FF00FF", # Magenta outline
                "stroke_width": 7,
                "max_chars_per_line": 26
            },
            "fire_text": {
                "font_size": 80,
                "color": "#FF4500",        # Orange red
                "stroke_color": "#FFFFFF", # White outline
                "stroke_width": 9,
                "max_chars_per_line": 25
            }
        }
        
        current_style = styles.get(style, styles["ultra_vibrant"])
        
        # Process transcript segments
        text_segments = []
        
        for segment in transcript_result["segments"]:
            if "words" in segment:
                words = segment["words"]
                word_groups = self._create_word_groups(words)
                
                for group in word_groups:
                    text = " ".join([w["word"] for w in group]).strip()
                    start_time = group[0]["start"]
                    end_time = group[-1]["end"]
                    
                    text_segments.append({
                        'text': text,
                        'start': start_time,
                        'end': end_time
                    })
        
        # Fix timing overlaps
        fixed_segments = self._fix_timing_overlaps(text_segments)
        
        # Create text clips
        for segment in fixed_segments:
            txt_clip = self._create_safe_text_clip(
                segment['text'],
                current_style,
                segment['start'],
                segment['duration']
            )
            
            if txt_clip:
                subtitle_clips.append(txt_clip)
                print(f"📝 Subtitle: '{segment['text'][:30]}...' ({segment['start']:.1f}s)")
        
        return subtitle_clips
    
    def _create_word_groups(self, words):
        """Group words for optimal subtitle display"""
        groups = []
        current_group = []
        
        for word in words:
            current_group.append(word)
            
            # Group 5-7 words together
            if len(current_group) >= 7:
                groups.append(current_group)
                current_group = []
            elif (len(current_group) >= 4 and 
                  word["word"].strip().endswith(('.', '!', '?', ','))):
                groups.append(current_group)
                current_group = []
        
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def _fix_timing_overlaps(self, segments):
        """Fix overlapping timing to prevent subtitle overlap"""
        if not segments:
            return []
        
        fixed_segments = []
        
        for i, segment in enumerate(segments):
            start_time = segment['start']
            original_end = segment['end']
            
            # Calculate ideal duration
            ideal_duration = max(self.min_display_time,
                               min(self.max_display_time, original_end - start_time))
            
            # Check overlap with next segment
            if i < len(segments) - 1:
                next_start = segments[i + 1]['start']
                max_end_time = next_start - self.min_gap_between_text
                
                if start_time + ideal_duration > max_end_time:
                    ideal_duration = max(0.5, max_end_time - start_time)
            
            final_duration = max(self.min_display_time, ideal_duration)
            
            fixed_segments.append({
                'text': segment['text'],
                'start': start_time,
                'duration': final_duration
            })
        
        return fixed_segments
    
    def _create_safe_text_clip(self, text, style, start_time, duration):
        """Create text clip with font fallback"""
        wrapped_text = self._smart_text_wrap(text, style["max_chars_per_line"])
        
        # Try fonts in order of reliability
        for font in self.safe_fonts:
            try:
                txt_clip = TextClip(
                    text=wrapped_text,
                    font_size=style["font_size"],
                    color=style["color"],
                    stroke_color=style["stroke_color"],
                    stroke_width=style["stroke_width"],
                    method='caption',
                    size=(self.safe_text_width, self.max_text_height),
                    text_align='center',
                    font=font
                )
                
                # Center vertically
                video_center_y = self.target_height // 2
                y_position = video_center_y - (txt_clip.h // 2)
                x_position = (self.target_width - self.safe_text_width) // 2
                
                return txt_clip.with_position((x_position, y_position)).with_start(start_time).with_duration(duration)
                
            except Exception:
                continue
        
        # If all fonts fail, try minimal approach
        try:
            simple_clip = TextClip(
                text=wrapped_text,
                font_size=style["font_size"],
                color=style["color"],
                method='caption',
                size=(self.safe_text_width, self.max_text_height),
                text_align='center'
            )
            
            y_position = (self.target_height - simple_clip.h) // 2
            x_position = (self.target_width - self.safe_text_width) // 2
            
            return simple_clip.with_position((x_position, y_position)).with_start(start_time).with_duration(duration)
            
        except Exception as e:
            print(f"⚠️ Could not create subtitle for: '{text}' - {e}")
            return None
    
    def _smart_text_wrap(self, text, max_chars_per_line):
        """Smart text wrapping for subtitles - no truncation"""
        wrapped_lines = textwrap.wrap(
            text,
            width=max_chars_per_line,
            break_long_words=False,
            break_on_hyphens=False
        )
        
        # Simply return all wrapped lines without truncation
        return '\n'.join(wrapped_lines)