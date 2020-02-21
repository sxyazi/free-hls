<?php

require 'functions.php';

$_POST['code'] = trim($_POST['code']);

if (!$_POST['code']) {
	fail('code cannot be empty');
} else if (strlen($_POST['code']) > 100*1024) {
	fail('code size cannot exceed 100K');
}


$file = md5($_POST['code']);
file_put_contents("data/{$file}", base64_encode($_POST['code']));

succ(['key' => $file, 'url' => "http://101.200.147.153:3395/play.php?key={$file}"]);
