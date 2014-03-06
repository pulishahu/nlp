<?php

$check_list = array("CD","EX","JJ","JJR", "JJS","MD","NN","NNS","NNPS","NNP","PDT","PRP","RBR","RBS","VB","VBD","VBG","VBN","VBP","VBZ","WDT","WP","WP$","WRB");
$removed_tags = array("are","is","that","such","have","will", "the", "they", "The", "has","he", "be","we","it");
$adj_words = array();
$reddit_link = "http://www.reddit.com/user/tldrrr";

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

    global $check_list, $removed_tags, $adj_words;
    $words = array();


    foreach ($tags as $key_word => $data){

        if(array_key_exists($data[0], $words)){
            $prop = $words[$data[0]];
            $prop[0]++;
        }
        else{
            $prop[0] = 1;
            $prop[1] = $data[1];
        }
        
        if(array_key_exists($data[0], $adj_words)){
            $adj = $adj_words[$data[0]];
        }
        else{
            $adj = array();
        }
        $pre_key = $key_word - 1;
        $pre_data = $tags[$pre_key];
        if($pre_data){
            if(array_key_exists($pre_data[0], $adj[0])){
                $adj[0][$pre_data[0]] += 1;
            }
            else{
                $adj[0][$pre_data[0]] = 1;
            }
        }
        $post_key = $key_word + 1;
        $post_data = $tags[$post_key];

        if($post_data){
            if(array_key_exists($post_data[0], $adj[1])){
                $adj[1][$post_data[0]] += 1;
            }
            else{
                $adj[1][$post_data[0]] = 1;
            }
        }

        $adj_words[$data[0]] = $adj;

        if(in_array($data[1], $check_list)){
            if(!in_array($data[0], $removed_tags)){
                $words[$data[0]] = $prop;
            }
        }
    }
    
    foreach($adj_words as $word => $adj) {
        $str = "";
        foreach($adj[0] as $pre_key => $value){
            $str .= "$pre_key($value), ";
        }
        $str .= "/";
        foreach($adj[1] as $post_key => $value){
            $str .= "$post_key($value), ";
        }
        $adj[3] = $str;
        //echo "key -> $word -> $str <br>" ;
        $adj_words[$word] = $adj;
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



function getPointedText($text, $tags){

    $arr = explode(".", $text);
    foreach($arr as $key =>  $line){
        foreach($tags as $tag){
            if( strripos($line, $tag) !== false){
                //$arr[$key] = str_ireplace($tag,"<strong><span class='text-danger'>$tag</span></strong>",$line);
                $arr[$key] = "<span class='text-success'>".$line."</span>";
            }
        }
    }

    foreach($arr as $key =>  $line){
        $count = 0;
        foreach($tags as $tag){
            if( strripos($line, $tag) !== false){
                //$arr[$key] = str_ireplace($tag,"<span class='text-success'>$tag</span>",$line);
              //  $arr[$key] = "<span class='text-success'>".$line."</span>";
                $count++;
            }
        }
        if($count  >  (count($tags) - 1)){
            //$arr[$key] = "<span class='text-danger'>".$line."</span>";
            //$arr[$key] = str_replace("text-success","text-danger",$line);
        }
    }


    $text = implode(".",$arr);
    return $text;
}


function reddit($text, $tags){

    $nn1 = false; $nn2 = false;
    $jj = false;

    foreach($tags as $tag => $prop){

        $pos = $prop[1];
        if($pos == "NNP"){
            if(!$nn1)  $nn1 = $tag;
        }

        if($pos == "NNPS"){
            if(!$nn2) $nn2 = $tag;
        }

        if( $pos == "JJ" || $pos == "JJR" || $pos == "JJS"){
            if(!$jj) $jj = $tag;
        }

        if($jj && $nn1 && $nn2) break;
    }

    echo $nn1." == ".$nn2." == ".$jj;


    $arr = explode(".", $text);
    foreach($arr as $key =>  $line){
        if(startsWith(trim($line), trim($nn1))){
            $arr[$key] = "<span class='text-danger'>".$line."</span>";
        }

        if( (strripos($line, $nn1) !== false) && (strripos($line, $jj) !== false)){
            $arr[$key] = "<span class='text-danger'>".$line."</span>";
        }
    }

    return implode(".",$arr);
}

function summeriseBot($text, $tags){

    global $removed_tags;

    $pos_tags = array(
        "NN1" => false,
        "NN2" => false,
        "JJ1" => false,
        "JJ2" => false
    );


    $nn1 = false; $nn2 = false;
    $jj1 = false; $jj2 = false;

    $nn1 = false; $nn2 = false;
    $jj1 = false; $jj2 = false;


    $nn_pos = array("NNS", "NNP","NNS","NNPS");
    $jj_pos = array("JJ", "JJR","JJS");

    foreach($tags as $tag => $prop){

        if(in_array($tag, $removed_tags)) continue;
        $ss = array("tag" => $tag, "freq" => $prop[0], "pos" => $prop[1]);
        $pos = $prop[1];
        if(in_array($pos, $nn_pos)){
            if(!is_array($pos_tags["NN1"])) $pos_tags["NN1"] = $ss;
            else $pos_tags["NN2"] = $ss;
        }
        if(in_array($pos, $jj_pos)){
            if(! is_array($pos_tags["JJ1"])) $pos_tags["JJ1"] = $ss;
            else $pos_tags["JJ2"] = $ss;
        }
        if($pos_tags["NN1"] && $pos_tags["NN2"] && $pos_tags["JJ1"] && $pos_tags["JJ2"]) break;
    }

    $points = array(); $order =0;
    $arr = explode("\n", $text);
    foreach($arr as $key =>  $line){
        foreach($pos_tags as $key => $data){
            if( strripos($line, $data["tag"]) !== false){
               $points[$line][$key] = $data;
            }
        }
    }


    /*foreach($points as $line => $data){
        $teaser_form = array();
        if( strripos($line, $pos_tags["JJ1"]) !== false){
            if(!$teaser_form["jj1"]) = $line;
        }
    }*/


    $str = "<ol>";
    foreach ($points as $line => $data){
        foreach($data as $pos => $prop){
            $line = str_ireplace($prop["tag"],"<strong>{$prop["tag"]}<small>[{$prop["freq"]}]({$prop["pos"]})</small></strong>",$line);
        }
        $str .="<li><h4>$line</h4></li>";
    }
    $str .="</ol>";
    return $str;

}


function startsWith($haystack, $needle)
{
        return $needle === "" || strpos($haystack, $needle) === 0;
}
?>
