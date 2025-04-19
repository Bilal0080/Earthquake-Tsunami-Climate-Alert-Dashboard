const express = require('express');
const multer = require('multer');
const sharp = require('sharp');
const app = express();
const upload = multer({ dest: 'uploads/' });

app.post('/compress', upload.single('image'), (req, res) => {
    const quality = parseFloat(req.body.quality);
    sharp(req.file.path)
        .jpeg({ quality: Math.floor(quality * 100) })
        .toBuffer()
        .then(data => {
            res.set('Content-Type', 'image/jpeg');
            res.send(data);
        })
        .catch(err => {
            res.status(500).send('Error compressing image');
        });
});

app.listen(3000, () => {
    console.log('Server running on port 3000');
});