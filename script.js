// script.js
document.getElementById('upload-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const file = document.getElementById('image-input').files[0];
    const compressionLevel = parseFloat(document.getElementById('compression-level').value);

    if (file) {
        compressImage(file, compressionLevel);
    }
});

function compressImage(file, quality) {
    const reader = new FileReader();
    reader.onload = function(event) {
        const img = new Image();
        img.src = event.target.result;

        img.onload = function() {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = img.width;
            canvas.height = img.height;
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

            canvas.toBlob(function(blob) {
                const compressedImageUrl = URL.createObjectURL(blob);
                document.getElementById('compressed-image').src = compressedImageUrl;
                document.getElementById('download-link').href = compressedImageUrl;
                document.getElementById('download-link').download = `compressed_${file.name}`;
            }, 'image/jpeg', quality);
        };
    };
    reader.readAsDataURL(file);
}