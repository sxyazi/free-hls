<?php

require 'functions.php';

$_POST['code'] = trim($_POST['code']);

if (!$_POST['code']) {
	fail('code cannot be empty');
} else if (strlen($_POST['code']) > 100*1024) {
	fail('code size cannot exceed 100K');
}


$file = md5($_POST['code']);
file_put_contents("data/{$file}", json_encode([
	'code'       => base64_encode($_POST['code']),
	'title'      => trim($_POST['title']) ?: 'untitled',
	'created_at' => time()
]));


succ([
	'key' => $file,
	'url' => "http://{$_SERVER['HTTP_HOST']}/play.php?key={$file}"
]);
