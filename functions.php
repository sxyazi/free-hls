<?php

function fail($err) {
	exit(json_encode(['code' => -1, 'err' => $err]));
}

function succ($data = null) {
	exit(json_encode(['code' => 0, 'data' => $data]));
}
