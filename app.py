from flask import Flask, render_template_string, request
from PIL import Image, ImageEnhance, ImageFilter
import io
import base64

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Photo Enhancer Pro</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); 
            min-height: 100vh; 
            color: white; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            padding: 20px;
        }
        .card { 
            background: rgba(255, 255, 255, 0.07); 
            backdrop-filter: blur(10px); 
            border: 1px solid rgba(255, 255, 255, 0.1); 
            border-radius: 20px; 
            padding: 25px; 
            width: 100%; 
            max-width: 420px; 
            box-shadow: 0 15px 35px rgba(0,0,0,0.5); 
            text-align: center;
        }
        h2 { 
            font-size: 24px; 
            font-weight: 700; 
            background: linear-gradient(45deg, #ff416c, #ff4b2b); 
            -webkit-background-clip: text; 
            -webkit-text-fill-color: transparent; 
            margin-bottom: 5px;
        }
        p.subtitle { font-size: 13px; color: #ccc; margin-bottom: 20px; }
        
        .placeholder-box {
            width: 100%;
            height: 280px;
            border: 2px dashed rgba(255,255,255,0.25);
            border-radius: 15px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            margin-bottom: 20px;
            background: rgba(0, 0, 0, 0.2);
        }
        .placeholder-box span { font-size: 40px; margin-bottom: 10px; }
        .placeholder-box p { font-size: 14px; color: #aaa; }

        .img-box { 
            position: relative; 
            width: 100%; 
            height: 320px; 
            margin-bottom: 15px; 
            overflow: hidden; 
            display: none; 
            border-radius: 15px; 
            box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        }
        .img-box img { width: 100%; height: 100%; object-fit: cover; position: absolute; top: 0; left: 0; }
        .after-img { clip-path: polygon(0 0, 50% 0, 50% 100%, 0 100%); }
        
        .tag {
            position: absolute;
            top: 12px;
            background: rgba(0, 0, 0, 0.65);
            color: #fff;
            padding: 4px 10px;
            font-size: 11px;
            font-weight: bold;
            border-radius: 20px;
            letter-spacing: 1px;
            z-index: 10;
            backdrop-filter: blur(4px);
            border: 1px solid rgba(255,255,255,0.2);
            pointer-events: none;
        }
        .tag-before { left: 12px; }
        .tag-after { right: 12px; color: #ff416c; }

        .slider { 
            width: 100%; 
            margin-bottom: 20px; 
            accent-color: #ff416c; 
            cursor: pointer;
        }
        
        input[type="file"] { display: none; }
        
        .btn-group { display: flex; gap: 10px; justify-content: center; }
        .btn { 
            background: linear-gradient(45deg, #ff416c, #ff4b2b); 
            color: white; 
            padding: 12px 20px; 
            border-radius: 30px; 
            border: none; 
            font-weight: 600; 
            font-size: 14px; 
            cursor: pointer; 
            box-shadow: 0 5px 15px rgba(255, 65, 108, 0.4);
            transition: 0.3s;
            text-decoration: none;
            display: inline-block;
        }
        .btn-download {
            background: linear-gradient(45deg, #11998e, #38ef7d);
            box-shadow: 0 5px 15px rgba(56, 239, 125, 0.3);
            display: none;
        }
    </style>
</head>
<body>
    <div class="card">
        <h2>AI Photo Enhancer</h2>
        <p class="subtitle">আপনার সাধারণ ছবিকে রূপ দিন Ultra HD লুক-এ</p>

        <div class="placeholder-box" id="placeholder">
            <span>📷</span>
            <p>গ্যালারি থেকে একটি ছবি আপলোড করুন</p>
        </div>

        <div class="img-box" id="imgBox">
            <div class="tag tag-before">BEFORE</div>
            <div class="tag tag-after">AFTER</div>
            <img id="beforeImg" src="" alt="Original">
            <img id="afterImg" class="after-img" src="" alt="After HD">
        </div>
        
        <input type="range" min="0" max="100" value="50" class="slider" id="slider" oninput="moveSlider(this.value)" style="display:none;">

        <form id="uploadForm">
            <div class="btn-group">
                <label class="btn" for="fileInput">ছবি নির্বাচন করুন</label>
                <input type="file" id="fileInput" name="image" accept="image/*" onchange="uploadImage()">
                <a id="downloadBtn" class="btn btn-download" download="enhanced_hd.jpg">সেভ করুন 📥</a>
            </div>
        </form>
    </div>

    <script>
        function uploadImage() {
            let formData = new FormData(document.getElementById('uploadForm'));
            fetch('/enhance', { method: 'POST', body: formData })
            .then(res => res.json())
            .then(data => {
                document.getElementById('beforeImg').src = data.original;
                document.getElementById('afterImg').src = data.enhanced;
                
                let downloadBtn = document.getElementById('downloadBtn');
                downloadBtn.href = data.enhanced;

                document.getElementById('placeholder').style.display = 'none';
                document.getElementById('imgBox').style.display = 'block';
                document.getElementById('slider').style.display = 'block';
                downloadBtn.style.display = 'inline-block';
            });
        }
        function moveSlider(val) {
            document.getElementById('afterImg').style.clipPath = `polygon(0 0, ${val}% 0, ${val}% 100%, 0 100%)`;
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/enhance', methods=['POST'])
def enhance():
    file = request.files['image']
    img = Image.open(file.stream).convert('RGB')

    smooth_base = img.filter(ImageFilter.GaussianBlur(radius=3))
    skin_retouched = Image.blend(img, smooth_base, alpha=0.55)

    enhancer_sharp = ImageEnhance.Sharpness(skin_retouched)
    img_sharp = enhancer_sharp.enhance(1.4)

    enhancer_bright = ImageEnhance.Brightness(img_sharp)
    img_bright = enhancer_bright.enhance(1.05)

    enhancer_color = ImageEnhance.Color(img_bright)
    img_color = enhancer_color.enhance(1.10)

    enhancer_contrast = ImageEnhance.Contrast(img_color)
    enhanced_img = enhancer_contrast.enhance(1.08)

    buffered_orig = io.BytesIO()
    img.save(buffered_orig, format="JPEG")
    orig_b64 = "data:image/jpeg;base64," + base64.b64encode(buffered_orig.getvalue()).decode('utf-8')

    buffered_enh = io.BytesIO()
    enhanced_img.save(buffered_enh, format="JPEG")
    enh_b64 = "data:image/jpeg;base64," + base64.b64encode(buffered_enh.getvalue()).decode('utf-8')

    return {'original': orig_b64, 'enhanced': enh_b64}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
