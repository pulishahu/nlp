<?php

include "functions.php";

if($_POST["text"]){
    file_write($_POST["text"]);
}


if($_POST["tags"]){
    $tags_element = $_POST["tags"];
}

$contents = getWords();
$words_data = json_decode($contents, true);
$tags = $words_data["tags"];
$raw_text = $words_data["para"];
$highlighted_text = getPointedText($raw_text, $tags_element);
$summarisedText = summeriseBot($raw_text, getWordSort($tags));

$reddit =  reddit($raw_text, getWordSort($tags));

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
<form role="form" method="POST">
<button type="submit" class="btn btn-default">Submit</button>
<div class="form-group">

<?

$words = getWordSort($tags);
echo "<ol>";
foreach($words as $key => $data){
    echo "<li>";
    echo "<div class='checkbox'><label><input type='checkbox' name='tags[]' value='$key'>";
    echo "<h4>$key<small>[{$data[0]}] ({$data[1]}) </small><h4>";
    echo "</label></div>";
    echo "</li>";
}
echo "</ol>";
?>
</form>
</div>

</div></div>
<!--sort end -->

</div>

<div class="col-md-8">
<?

echo "<div class='section'><div class='container'>";
//echo "<h4>$reddit</h4>";
echo "$summarisedText";
//echo "<h4>$highlighted_text</h4>";
echo "</div></div>";

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
