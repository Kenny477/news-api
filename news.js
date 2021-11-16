const express = require('express');
const app = express();
const PORT = 8080;

app.use(express.json());

app.listen(
    PORT,
    () => console.log(`Node.js server running on http://localhost:${PORT}`)
)

app.get('/news', (req, res) => {
    let spawn = require("child_process").spawn;
    let process = spawn('python', ["news.py",
        req.query.endpoint,
        req.query.n_articles
    ]);
    process.stdout.on('data', (data) => {
        res.status(200).send(data.toString());
    });
    process.on('close', (code) => {
        console.log(`child process exited with code ${code}`);
    });
})