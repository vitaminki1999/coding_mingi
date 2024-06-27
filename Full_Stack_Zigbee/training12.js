const express = require('express');
const mysql = require('mysql');

const app = express();

// MySQL 연결 설정 (기존 코드와 동일)
const connection = mysql.createConnection({
    host: 'svc.sel5.cloudtype.app',
    port: 32712,
    user: 'root',
    password: '2024320319',
    database: 'new_schema'
});

// 뷰 엔진 설정
app.set('view engine', 'ejs');
app.set('views', __dirname + '/views'); // 템플릿 파일 경로 설정

app.get('/', (req, res) => {
  connection.query('SELECT * FROM new_table2 ORDER BY NUM1 DESC LIMIT 100', (error, results) => {
    if (error) throw error;

    // 시간 변환 (기존 코드와 동일)
    results.forEach(row => {
      const utcTime = new Date(row.time);
      const kstTime = utcTime.toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' });
      row.time = kstTime;
    });

    res.render('index', { data: results }); // index.ejs 템플릿 렌더링 및 데이터 전달
  });
});

app.get('/soge', function(req, res) {
    res.sendFile(__dirname + '/soge.ejs');
});

app.get('/bog', function(req, res) {
    res.sendFile(__dirname + '/bog.html');
});

app.listen(3000, () => {
  console.log('Server is running on port 3000');
});



