<?php
function getWords(){

    $filename = "words.json";
    $handle = fopen($filename, "r");
    $contents = fread($handle, filesize($filename));
    fclose($handle);
    return $contents;
}

function gettest(){

    $filename = "test.json";
    $handle = fopen($filename, "r");
    $contents = fread($handle, filesize($filename));
    fclose($handle);
    return $contents;
}

$testdata = gettest();
$testdata = json_decode($testdata, true);

$contents = getWords();
$words_data = json_decode($contents, true);
?>

<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head> 
<body>

<?php


foreach($testdata as $key => $value){

    echo "<br> $key <br> $value<br><br>";
}


$words = $words_data["words"];
foreach ($words as $key_word => $data){
    echo "$key_word [";
    foreach ($data as $key => $value){
    echo "$key , ";
    }
    echo "]<br>";
}

?>


</body>
</html>
