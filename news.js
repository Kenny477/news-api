const express = require('express');
const app = express();
const PORT = 8080;

app.use(express.json());

app.listen(
    PORT,
    () => console.log(`it's alive on http://localhost:{$PORT}`)
)

app.get('/news', (req, res) => {
    res.status(200).send({
        source: 'nyt',
        headline: 'Cool stuff'
    })
})