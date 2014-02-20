<?php
function getWords(){

    $filename = "words.json";
    $handle = fopen($filename, "r");
    $contents = fread($handle, filesize($filename));
    fclose($handle);
    return $contents;
}

$contents = getWords();
$words_data = json_decode($contents, true);
?>

<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head> 
<body>

<?php

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
