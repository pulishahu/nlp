<?php

$check_list = array("CD","EX","JJ","JJR", "JJS","MD","NN","NNS","NNPS","NNP","PDT","PRP","RBR","RBS","VB","VBD","VBG","VBN","VBP","VBZ","WDT","WP","WP$","WRB");

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

    global $check_list;
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
            if(in_array($data[1], $check_list)){
                $words[$data[0]] = $prop;
            }
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



function getPointedText($text, $tags){
    
    $tags[] = "Egypt's";
    $arr = explode(".", $text);
    foreach($arr as $key =>  $line){
        foreach($tags as $tag){
            if( strripos($line, $tag) !== false){
                //$arr[$key] = str_ireplace($tag,"<strong><span class='text-danger'>$tag</span></strong>",$line);
                //$arr[$key] = "<span class='text-success'>".$line."</span>";
            } 
        }
    }
    
    foreach($arr as $key =>  $line){
        $count = 0;
        foreach($tags as $tag){
            if( strripos($line, $tag) !== false){
                //$arr[$key] = str_ireplace($tag,"<span class='text-success'>$tag</span>",$line);
                $arr[$key] = "<span class='text-success'>".$line."</span>";
                $count++;
            } 
        }
        if($count  >  (count($tags) - 1)){
            $arr[$key] = "<span class='text-danger'>".$line."</span>";
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
        if( $pos == "NNP" || $pos == "NNPS"){
            if(!$nn1)  $nn = $tag; 
            else {
                if(!$nn2) $nn2 = $tag; 
            }
        }        

        if( $pos == "JJ" || $pos == "JJR" || $pos = "JJS"){
            if(!$jj) $jj = $tag;
        }

        if($jj && $nn1 && $nn2) break;
    }


    $arr = explode(".", $text);
    foreach($arr as $key =>  $line){
        if(startsWith($line, $nn1)){
            $arr[$key] = "<span class='text-danger'>".$line."</span>";
        }  

        if( (strripos($line, $nn1) !== false) && (strripos($line, $jj) !== false)){
            $arr[$key] = "<span class='text-danger'>".$line."</span>";
        }
    }
}


function startsWith($haystack, $needle)
{
        return $needle === "" || strpos($haystack, $needle) === 0;
}
?>
