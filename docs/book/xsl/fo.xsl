<?xml version="1.0" encoding="utf-8"?>

<!--

   XSL-FO specific stylesheet.

   This is intended to be used for generating PDF files (although
   potentially, it could be useful elsewhere)

-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns:fo="http://www.w3.org/1999/XSL/Format"
                version="1.0">

  <xsl:import href="http://docbook.sourceforge.net/release/xsl/current/fo/docbook.xsl"/>
 
  <!-- Include docbook that is common to all output -->
  <xsl:include href="common.xsl"/>

  <!-- Include our custom title page -->
  <xsl:include href="fo-titlepage.xsl"/>

  <xsl:param name="monospace.font.family"
	     select="'monospace,ZapfDingbats'"/>

  <xsl:param name="toc.section.depth" select="1" />
  <xsl:param name="glossary.as.blocks" select="1" />


  <!-- format lineoutput better -->
  <xsl:attribute-set name="monospace.verbatim.properties"
                     use-attribute-sets="verbatim.properties">

    <xsl:attribute name="text-align">start</xsl:attribute>
    <xsl:attribute name="wrap-option">wrap</xsl:attribute>

    <xsl:attribute name="font-family">
      <xsl:value-of select="$monospace.font.family"/>
    </xsl:attribute>

    <xsl:attribute name="font-size">
      <xsl:value-of select="$body.font.master * 0.7"/>
      <xsl:text>pt</xsl:text>
    </xsl:attribute>

    <xsl:attribute name="border-color">#8fbc8f</xsl:attribute>
    <xsl:attribute name="border-style">solid</xsl:attribute>
    <xsl:attribute name="border-width">thin</xsl:attribute>
    <xsl:attribute name="padding">7pt</xsl:attribute>

    <xsl:attribute name="background-color">
      <xsl:choose>
	<xsl:when test="self::programlisting">#FFFFF8</xsl:when>
	<xsl:otherwise>#FDFFFD</xsl:otherwise>
      </xsl:choose>
    </xsl:attribute>
  </xsl:attribute-set>


  <xsl:param name="refentry.pagebreak" select="0"/>
  <xsl:param name="body.start.indent" select="'0pc'"/>
  <xsl:param name="body.start.indent" select="'0pc'"/>
  <xsl:param name="page.margin.inner" select="'2.5cm'"/>
  <xsl:param name="page.margin.outer" select="'2.5cm'"/>
  <xsl:param name="body.font.master" select="11"/>
  <xsl:param name="shade.verbatim" select="1"/>

  <xsl:param name="fop1.extensions" select="1"/>

  <xsl:param name="generate.toc">
    appendix  toc,title
    article/appendix  nop
    article   toc,title
    book      toc,title
    chapter   nop
    part      toc
    preface   toc,title
    qandadiv  toc
    qandaset  toc
    reference nop
    set       toc,title
  </xsl:param>


  <!--  Use the body text font, but in italics  -->
  <xsl:template match="lineannotation">
    <fo:inline font-family="{$body.font.family}"
               font-style="italic">
      <xsl:call-template name="inline.charseq"/>
    </fo:inline>
  </xsl:template>
  

  <!-- Support tables with tabstyle='small' -->
  <xsl:attribute-set name="table.table.properties">
    <xsl:attribute name="font-size">
      <xsl:choose>
	<xsl:when test="ancestor-or-self::table[1]/@tabstyle='small' or
			ancestor-or-self::informaltable[1]/@tabstyle='small'">
	  <xsl:value-of select="$body.font.master * 0.7"/><xsl:text>pt</xsl:text>
	</xsl:when>
	<xsl:otherwise>inherit</xsl:otherwise>
      </xsl:choose>
    </xsl:attribute>
  </xsl:attribute-set>


  <!-- Skip certain material from the PDF Bookmark/Contents -->
 <xsl:template match="section" mode="fop1.outline" />


 <!-- From:
 http://www.sagehill.net/docbookxsl/PrintToc.html#PartToc
 -->
 <!-- Generate TOC for part as part of part titlepage -->
 <xsl:template name="part.titlepage.before.verso" priority="1">
   <xsl:variable name="toc.params">
     <xsl:call-template name="find.path.params">
       <xsl:with-param name="table"
		       select="normalize-space($generate.toc)"/>
     </xsl:call-template>
   </xsl:variable>
   <xsl:if test="contains($toc.params, 'toc')">
     <xsl:call-template name="division.toc">
       <xsl:with-param name="toc.context" select="."/>
     </xsl:call-template>
   </xsl:if>
 </xsl:template>

 <!-- Switch off the original  part toc page-sequence template -->
 <xsl:template name="generate.part.toc"/>
  
</xsl:stylesheet>
