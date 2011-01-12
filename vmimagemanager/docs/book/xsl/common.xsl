<?xml version="1.0" encoding="utf-8"?>


<!--  Common XSL 

  These declarations are common to all output formats.
 -->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">

  <!-- Parameters -->
  <xsl:param name="refentry.generate.name" select="0"/>
  <xsl:param name="refentry.generate.title" select="1"/>
  <xsl:param name="refentry.xref.manvolnum" select="0"/>

  <xsl:param name="generate.section.toc.level" select="0"/>
 
  <xsl:param name="draft.mode" select="'no'"/>
  <xsl:param name="draft.watermark.image" select="''"/>


  <!-- Convert typed "straight" apostrophes to the "curly" type if in a para or title -->
  <xsl:template match="para/text()|title/text()">
    <xsl:value-of select="translate(.,&quot;&apos;&quot;,&apos;&#x2019;&apos;)"/>
  </xsl:template>
  <xsl:template match="para/text()|title/text()" mode="no.anchor.mode">
    <xsl:value-of select="translate(.,&quot;&apos;&quot;,&apos;&#x2019;&apos;)"/>
  </xsl:template>


  <!-- Work-around where the DTD automatically adds class="trade" -->
 <xsl:template match="productname">
   <xsl:call-template name="inline.charseq"/>
   <xsl:if test="@class != 'trade' or (@class = 'trade' and @role='showmark')">
     <xsl:call-template name="dingbat">
       <xsl:with-param name="dingbat" select="@class"/>
     </xsl:call-template>
   </xsl:if>
 </xsl:template>


 <!-- Support for <phrase role='math'>equation</phrase> -->
 <xsl:template match="phrase[@role = 'math']">
   <xsl:call-template name="inline.italicseq"/>
 </xsl:template>


 <!-- Allow us to remove certain sections from the TOC -->
 <xsl:template match="section[@role = 'NotInToc']" mode="toc" />

</xsl:stylesheet>
