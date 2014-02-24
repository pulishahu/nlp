<?php

$check_list = array("CD","EX","JJ","JJR", "JJS","MD","NN","NNS","NNPS","PDT","PRP","RBR","RBS","VB","VBD","VBG","VBN","VBP","VBZ","WDT","WP","WP$","WRB");

if($_POST["text"]){
    file_write($_POST["text"]);
}


function getWords(){

    $filename = "corp.json";
    $handle = fopen($filename, "r");
    $contents = fread($handle, filesize($filename));
    fclose($handle);
    return $contents;
}

function file_write($str){
    $file = fopen("raw_text.txt","w");
    fwrite($file,$str);
    fclose($file);
}

function getWordFreq($tags){
    $words = array();
    foreach ($tags as $key_word => $data){
        if(array_key_exists($data[0], $words)){
            $prop = $words[$data[0]];
            $prop[0]++;
            $words[$data[0]] = $prop;
        }
        else{
            $prop[0] = 1;
            $prop[1] = $data[1];
            $words[$data[0]] = $prop;
        }
    }
    return $words;
}

function getWordSort($tags){
    
    $words = array();
    foreach ($tags as $key_word => $data){
        if(array_key_exists($data[0], $words)){
            $prop = $words[$data[0]];
            $prop[0]++;
            $words[$data[0]] = $prop;
        }
        else{
            $prop[0] = 1;
            $prop[1] = $data[1];
            $words[$data[0]] = $prop;
        }
    }

    foreach($words as $key => $row) {                                            
        $volume[$key]  = $row[0];                                    
        $edition[$key] = $row[1];                                   
    }  

    array_multisort($volume, SORT_DESC, $edition, SORT_ASC, $words);
    return $words; 
}

function texttagReplace($tags, $raw_text){
    global $check_list;
    $words = getWordFreq($tags);
    foreach ($words as $key => $data){
        if(in_array($data[1], $check_list)){
            $match = " $key<small>[{$data[0]}] ({$data[1]})</small> ";
            $raw_text = str_replace(" $key ", $match , $raw_text);
        }
    }
    return "<h4>$raw_text</h4>";
}


function getTaggedSentence($tags){
    $tag_str = "<h4>";
    foreach ($tags as $key_word => $data){
        $tag_str .= $data[0]."<small>({$data[1]})</small> ";  
    }
    $tag_str .= "</h4>";
    return $tag_str;
}

$contents = getWords();
$words_data = json_decode($contents, true);
$tags = $words_data["tags"];
$raw_text = $words_data["para"];


include "header.php";
?>

<div class="row">
<div class="col-md-1">

</div>
<div class="col-md-3">

<div><div>
<form role="form" method="POST">
  <div class="form-group">
    <label for="exampleInputEmail1">Enter raw text</label>
<textarea class="form-control" rows="5" name="text"></textarea>
    </div>
<button type="submit" class="btn btn-default">Submit</button>
</form>
</div></div>

<!--Sorted Words -->
<div><div class='container'>
<?

$words = getWordSort($tags);
echo "<ol>";
foreach($words as $key => $data){
echo "<li><h4>$key<small>[{$data[0]}] ({$data[1]}) </small><h4></li>";
}    
echo "</ol>";
?>
</div></div>
<!--sort end -->

</div>

<div class="col-md-8">
<?

$tag_str = getTaggedSentence($tags);
echo "<div class='section'><div class='container'>";
echo $tag_str;
echo "</div></div>";

$str = texttagReplace($tags, $raw_text); 
echo "<div class='section'><div class='container'>";
echo $str;
echo "</div></div>";

?>
</div>


</div>
</body>
</html>
