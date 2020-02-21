<?php

require 'functions.php';

$file = "data/{$_GET['key']}";

if (!is_file($file)) {
	fail('Key does not exist');
}

$code = file_get_contents($file);
require 'play.html';
