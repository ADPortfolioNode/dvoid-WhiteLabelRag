<?php
/**
 * Plugin Name: WhiteLabel RAG Embed
 * Plugin URI: https://stainlessdeoism.biz
 * Description: Embed your deployed WhiteLabel-RAG app via shortcode.
 * Version: 1.0
 * Author: 'Deoism' Anthony Dickerson
 * Author URI: https://stainlessdeoism.biz
 * License: GPL2+
 */

if ( ! defined( 'ABSPATH' ) ) exit; // Exit if accessed directly

// === Config ===
// Replace with your actual domain or Render/Fly URL
define( 'WHITELABEL_RAG_URL', 'https://a219utouyu2ya5c8tu52dyjwx.onrender.com' );

// === Shortcode ===
function whitelabelrag_embed_iframe() {
    $iframe = '<iframe src="' . WHITELABEL_RAG_URL . '" ';
    $iframe .= 'style="width:100%; height:600px; border:none;" ';
    $iframe .= 'loading="lazy"></iframe>';
    return $iframe;
}
add_shortcode( 'whitelabelrag', 'whitelabelrag_embed_iframe' );

?>
