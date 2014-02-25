<?php

include "functions.php";

if($_POST["text"]){
    file_write($_POST["text"]);
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
