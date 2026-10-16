import cv2, subprocess, os, time
import numpy as np

def build_loop(src_name, loop_id, crop_type, mask_type):
    print(f"\n==========================================")
    print(f"Building Real Floral Loop {loop_id} from {src_name}...")
    start_time = time.time()
    
    src_path = os.path.join('/root/dreamheights-source/videos', src_name)
    cap = cv2.VideoCapture(src_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open {src_path}")
        
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    target_frames = 144  # 6.0 seconds @ 24fps
    crossfade_len = 24  # 1.0 second crossfade
    total_needed = target_frames + crossfade_len
    
    # Seek 1.5 seconds in to skip any opening camera setup
    start_frame = int(fps * 1.5)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    
    raw_frames = []
    for _ in range(total_needed):
        ret, frame = cap.read()
        if not ret:
            # If video ended, loop from beginning
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()
            if not ret:
                break
        
        h, w = frame.shape[:2]
        size = min(h, w)
        if crop_type == 'top_left':
            cropped = frame[0:size, 0:size]
        elif crop_type == 'bottom':
            cropped = frame[h-size:h, 0:size]
        elif crop_type == 'center':
            y_off = (h - size) // 2
            x_off = (w - size) // 2
            cropped = frame[y_off:y_off+size, x_off:x_off+size]
        else:
            cropped = frame[0:size, 0:size]
            
        resized = cv2.resize(cropped, (720, 720), interpolation=cv2.INTER_AREA)
        hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
        
        # Segment plant from background
        if mask_type == 'sky_white':
            # Sky is bright and unsaturated
            is_plant = ~((hsv[:,:,2] > 200) & (hsv[:,:,1] < 45))
        elif mask_type == 'sky_blue':
            # Blue sky
            is_plant = ~((hsv[:,:,0] >= 85) & (hsv[:,:,0] <= 135) & (hsv[:,:,1] > 25))
        elif mask_type == 'wall_light':
            # Bougainvillea on wall
            is_boug = ((hsv[:,:,0] >= 135) & (hsv[:,:,1] > 30)) | ((hsv[:,:,0] <= 18) & (hsv[:,:,1] > 35))
            is_leaf = (hsv[:,:,0] >= 22) & (hsv[:,:,0] <= 95) & (hsv[:,:,1] > 25)
            is_dark = hsv[:,:,2] < 65
            is_plant = is_boug | is_leaf | is_dark
        elif mask_type == 'boug_vivid':
            is_boug = ((hsv[:,:,0] >= 135) & (hsv[:,:,1] > 35)) | ((hsv[:,:,0] <= 18) & (hsv[:,:,1] > 40))
            is_leaf = (hsv[:,:,0] >= 25) & (hsv[:,:,0] <= 95) & (hsv[:,:,1] > 30)
            is_branch = (hsv[:,:,2] < 70) & (hsv[:,:,1] < 100)
            is_plant = is_boug | is_leaf | is_branch
        elif mask_type == 'yellow_tree':
            is_plant = ~((hsv[:,:,2] > 195) & (hsv[:,:,1] < 45))
        else:
            # General daylight
            is_plant = ~((hsv[:,:,2] > 185) & (hsv[:,:,1] < 40))
            
        mask = (is_plant.astype(np.uint8) * 255)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.GaussianBlur(mask, (7, 7), 0)
        
        # Multiply by mask factor so background is pure #000000 black
        alpha_factor = (mask.astype(np.float32) / 255.0)[:, :, np.newaxis]
        black_bg = (resized.astype(np.float32) * alpha_factor).astype(np.uint8)
        raw_frames.append(black_bg)
        
    cap.release()
    
    # Seamless loop crossfade
    looped = []
    for i in range(target_frames):
        if i < crossfade_len:
            t = i / float(crossfade_len)
            f_end = raw_frames[target_frames + i]
            f_start = raw_frames[i]
            blended = cv2.addWeighted(f_end, 1.0 - t, f_start, t, 0)
            looped.append(blended)
        else:
            looped.append(raw_frames[i])
            
    # Write intermediate raw AVI
    tmp_avi = f'/root/dreamheights-source/videos/tmp_loop_{loop_id}.avi'
    out_mp4 = f'/root/dreamheights-source/videos/real-floral-loop-{loop_id}.mp4'
    out_webm = f'/root/dreamheights-source/videos/real-floral-loop-{loop_id}.webm'
    out_poster = f'/root/dreamheights-source/videos/real-floral-loop-{loop_id}_poster.webp'
    
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    writer = cv2.VideoWriter(tmp_avi, fourcc, 24, (720, 720))
    for f in looped:
        writer.write(f)
    writer.release()
    
    # Encode web-ready H.264 MP4
    cmd_mp4 = [
        'ffmpeg', '-y', '-i', tmp_avi,
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
        '-an', out_mp4
    ]
    subprocess.run(cmd_mp4, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Encode fast VP9 WebM
    cmd_webm = [
        'ffmpeg', '-y', '-i', tmp_avi,
        '-c:v', 'libvpx-vp9', '-deadline', 'realtime', '-cpu-used', '8',
        '-threads', '8', '-b:v', '1200k',
        '-an', out_webm
    ]
    subprocess.run(cmd_webm, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Generate crisp poster WebP
    cmd_poster = [
        'ffmpeg', '-y', '-ss', '0', '-i', out_mp4,
        '-vframes', '1', '-q:v', '75', out_poster
    ]
    subprocess.run(cmd_poster, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    if os.path.exists(tmp_avi):
        os.remove(tmp_avi)
        
    elapsed = time.time() - start_time
    print(f"✓ Loop {loop_id} complete in {elapsed:.1f}s | MP4: {os.path.getsize(out_mp4)/1024:.0f}KB | WebM: {os.path.getsize(out_webm)/1024:.0f}KB | Poster: {os.path.getsize(out_poster)/1024:.0f}KB")

if __name__ == '__main__':
    configs = [
        ('real_boug_sky_20593.mp4', '01', 'top_left', 'sky_white'),
        ('real_bougainvillea_wind.webm', '02', 'top_left', 'wall_light'),
        ('real_white_breeze_1187.mp4', '03', 'center', 'sky_blue'),
        ('real_pink_breeze_1168.mp4', '04', 'bottom', 'sky_blue'),
        ('real_boug_close_20674.mp4', '05', 'top_left', 'boug_vivid'),
        ('real_yellow_tree_1173.mp4', '06', 'center', 'yellow_tree'),
        ('real_pink_small_1186.mp4', '07', 'bottom', 'sky_blue'),
        ('real_nature_bloom_2854.mp4', '08', 'top_left', 'nature_light')
    ]
    
    for src, loop_id, crop, mask in configs:
        build_loop(src, loop_id, crop, mask)
        
    print("\n✓ ALL 8 REAL FLORAL LOOPS GENERATED SUCCESSFULLY!")
