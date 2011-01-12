<?xml version="1.0" encoding="utf-8"?>

<!DOCTYPE stylesheet [
   <!ENTITY % build-entities SYSTEM "../build-entities.xml">
   %build-entities;
]>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">

  <xsl:import href="http://docbook.sourceforge.net/release/xsl/current/html/docbook.xsl"/>

  <xsl:include href="common.xsl"/>
  <xsl:include href="html-common.xsl"/>

  <xsl:template name="user.header.content">
    <xsl:comment>#include virtual="&location-l3-template;"</xsl:comment>
  </xsl:template>

  <xsl:template name="user.footer.content">
    <xsl:comment>#include virtual="&location-frag-footer;"</xsl:comment>
  </xsl:template>


  <!--
      The following supports links to top-of-page, from:
      http://www.sagehill.net/docbookxsl/ReturnToTop.html
  -->
  <xsl:template name="section.titlepage.before.recto">
    <xsl:variable name="top-anchor">
      <xsl:call-template name="object.id">
	<xsl:with-param name="object" select="/*[1]"/>
      </xsl:call-template>
    </xsl:variable>

    <p class="returntotop">
      <xsl:text>[</xsl:text>
      <a href="#{$top-anchor}">
	<xsl:text>return to top</xsl:text>
      </a>
      <xsl:text>]</xsl:text>
    </p>
  </xsl:template>

</xsl:stylesheet>
