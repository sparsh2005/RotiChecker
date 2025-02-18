document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide icons
    lucide.createIcons();
  
    // DOM Elements
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');
    const uploadPlaceholder = document.getElementById('uploadPlaceholder');
    const imagePreview = document.getElementById('imagePreview');
    const uploadedImage = document.getElementById('uploadedImage');
    const newImageBtn = document.getElementById('newImageBtn');
    const analysisResults = document.getElementById('analysisResults');
    const roundnessScore = document.getElementById('roundnessScore');
    const colorScore = document.getElementById('colorScore');
    const totalScore = document.getElementById('totalScore');
    const feedbackText = document.getElementById('feedbackText');
  
    // Add new DOM element reference
    const useCameraButton = document.querySelector('.use-camera-button');
  
    // Add camera handling functions
    let stream = null;
  
    // Event Listeners
    uploadPlaceholder.addEventListener('click', () => fileInput.click());
    newImageBtn.addEventListener('click', () => fileInput.click());
    
    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
      e.preventDefault();
      uploadPlaceholder.style.borderColor = '#ffb74d';
    });
  
    uploadArea.addEventListener('dragleave', (e) => {
      e.preventDefault();
      uploadPlaceholder.style.borderColor = '#ffe0b2';
    });
  
    uploadArea.addEventListener('drop', (e) => {
      e.preventDefault();
      uploadPlaceholder.style.borderColor = '#ffe0b2';
      const file = e.dataTransfer.files[0];
      if (file && file.type.startsWith('image/')) {
        handleImageUpload(file);
      }
    });
  
    fileInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) {
        handleImageUpload(file);
      }
    });
  
    // Camera button click handler
    useCameraButton.addEventListener('click', async () => {
        try {
            // Get camera access with appropriate constraints
            const constraints = {
                video: {
                    facingMode: isMobile() ? 'environment' : 'user',
                    width: { ideal: 1920 },
                    height: { ideal: 1080 }
                }
            };
            
            stream = await navigator.mediaDevices.getUserMedia(constraints);
            
            // Create and show camera UI
            const cameraUI = createCameraUI();
            document.querySelector('.main-card').appendChild(cameraUI);
            
            // Start video stream
            const videoElement = document.getElementById('camera-feed');
            videoElement.srcObject = stream;
            
        } catch (err) {
            console.error('Camera access error:', err);
            alert('Unable to access camera. Please make sure you have granted camera permissions.');
        }
    });
  
    // Handle image upload
    function handleImageUpload(file) {
      // Show a preview in the UI
      const reader = new FileReader();
      reader.onloadend = () => {
        uploadedImage.src = reader.result;
        uploadPlaceholder.classList.add('hidden');
        imagePreview.classList.remove('hidden');
        // We'll reveal the analysis section after we get server results
        // but for a smooth user experience, let's keep the analysis visible:
        analysisResults.classList.remove('hidden');
  
        // Actually send the file to the server for real analysis
        sendImageToServer(file);
      };
      reader.readAsDataURL(file);
    }
  
    function sendImageToServer(file) {
      const formData = new FormData();
      formData.append('roti_image', file);
  
      fetch('/upload', {
        method: 'POST',
        body: formData
      })
      .then(async (response) => {
        if (!response.ok) {
          let errMsg = 'Error uploading image';
          try {
            const errorData = await response.json();
            if (errorData.error) errMsg = errorData.error;
          } catch (err) {}
          throw new Error(errMsg);
        }
        return response.json();
      })
      .then(data => {
        // data: { roundness: ..., color: ..., overall: ... }
        const { roundness, color, overall } = data;
        // Animate scores
        animateScore(roundnessScore, roundness);
        animateScore(colorScore, color);
        animateScore(totalScore, overall);
        // Color them
        updateScoreColor(roundnessScore, roundness);
        updateScoreColor(colorScore, color);
        updateScoreColor(totalScore, overall);
        // Feedback
        updateFeedback(overall);
      })
      .catch(error => {
        console.error('Upload error:', error);
        feedbackText.textContent = 'Oops! ' + error.message;
        analysisResults.classList.remove('hidden');
      });
    }
  
    // Animate score counting up
    function animateScore(element, target) {
      let current = 0;
      const increment = target / 50; 
      const animation = setInterval(() => {
        current += increment;
        if (current >= target) {
          current = target;
          clearInterval(animation);
        }
        element.textContent = Math.floor(current) + '%';
      }, 20);
    }
  
    // Update score color based on value
    function updateScoreColor(element, score) {
      element.classList.remove('good', 'medium', 'poor');
      if (score >= 90) {
        element.classList.add('good');
      } else if (score >= 70) {
        element.classList.add('medium');
      } else {
        element.classList.add('poor');
      }
    }
  
    // Update feedback message
    function updateFeedback(score) {
      let message;
      if (score >= 90) {
        message = "Perfect roti! You're a master chef! 👨‍🍳";
      } else if (score >= 70) {
        message = "Good effort! Keep practicing for perfection. 👍";
      } else {
        message = "Needs improvement. Try rolling more evenly. 💪";
      }
      feedbackText.textContent = message;
    }
  
    // Helper function to check if device is mobile
    function isMobile() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }
  
    // Create camera UI elements
    function createCameraUI() {
        const container = document.createElement('div');
        container.className = 'camera-container';
        container.innerHTML = `
            <div class="camera-wrapper">
                <video id="camera-feed" autoplay playsinline></video>
                <div class="camera-controls">
                    <button id="capture-button" class="capture-button">
                        <i data-lucide="circle"></i>
                    </button>
                </div>
                <button id="close-camera" class="close-camera">
                    <i data-lucide="x"></i>
                </button>
            </div>
        `;

        // Initialize new Lucide icons
        lucide.createIcons({
            attrs: {
                class: "camera-icon"
            }
        });

        // Add event listeners for camera controls
        const closeBtn = container.querySelector('#close-camera');
        const captureBtn = container.querySelector('#capture-button');

        closeBtn.addEventListener('click', () => {
            stopCamera();
            container.remove();
        });

        captureBtn.addEventListener('click', () => {
            captureImage();
        });

        return container;
    }
  
    // Stop camera stream
    function stopCamera() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
    }
  
    // Capture image from camera
    function captureImage() {
        const video = document.getElementById('camera-feed');
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        const context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Convert to file
        canvas.toBlob((blob) => {
            const file = new File([blob], "roti-camera.jpg", { type: "image/jpeg" });
            
            // Stop camera and remove UI
            stopCamera();
            document.querySelector('.camera-container').remove();
            
            // Process image using existing upload handler
            handleImageUpload(file);
        }, 'image/jpeg', 0.8);
    }
  });