<?xml version="1.0" encoding="utf-8"?>

<!DOCTYPE stylesheet [
   <!ENTITY % build-entities SYSTEM "../build-entities.xml">
   %build-entities;
]>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">

  <!--
  <xsl:import href="http://docbook.sourceforge.net/release/xsl/current/html/chunk.xsl"/>
  -->
  <xsl:import href="http://docbook.sourceforge.net/release/xsl/current/html/chunkfast.xsl"/>

  <xsl:include href="common.xsl"/>
  <xsl:include href="html-common.xsl"/>

  <!-- Parameters -->
  <xsl:param name="chunker.output.encoding" select="'ASCII'"/>
  <xsl:param name="chunk.separate.lots" select="1" />
  <xsl:param name="chunk.first.sections" select="1" />
  <xsl:param name="use.id.as.filename" select="1"/>

  <!--
      The following supports links to top-of-page.  This is a modified
      version from:
      http://www.sagehill.net/docbookxsl/ReturnToTop.html
  -->
  <xsl:template name="section.titlepage.before.recto">
    <xsl:variable name="level">
      <xsl:call-template name="section.level"/>
    </xsl:variable>

    <xsl:variable name="chunkfn">
      <xsl:apply-templates mode="recursive-chunk-filename" select="."/>
    </xsl:variable>

    <xsl:if test="$level &gt; $chunk.section.depth">
      <p class="returntotop">
	<xsl:text>[</xsl:text>
	<a href="{$chunkfn}">
	  <xsl:text>return to top</xsl:text>
	</a>
	<xsl:text>]</xsl:text>
      </p>
    </xsl:if>
  </xsl:template>


  <!--
      The following adds support for generate breadcrumbs.  Taken
      from: http://www.sagehill.net/docbookxsl/HTMLHeaders.html
  -->
  <xsl:template name="breadcrumbs">
    <xsl:param name="this.node" select="."/>
    <div class="breadcrumbs">
      <xsl:for-each select="$this.node/ancestor::*">
	<span class="breadcrumb-link">
	  <a>
	    <xsl:attribute name="href">
	      <xsl:call-template name="href.target">
		<xsl:with-param name="object" select="."/>
		<xsl:with-param name="context" select="$this.node"/>
	      </xsl:call-template>
	    </xsl:attribute>
	    <xsl:apply-templates select="." mode="title.markup"/>
	  </a>
	</span>
	<xsl:text> &gt; </xsl:text>
      </xsl:for-each>

      <!-- And display the current node, but not as a link -->
      <span class="breadcrumb-node">
	<xsl:apply-templates select="$this.node" mode="title.markup"/>
      </span>
    </div>
  </xsl:template>


  <!-- Customise our HTML content, after std. navigation header -->
  <xsl:template name="user.header.content">
    <xsl:if test="boolean(../..)">
      <xsl:call-template name="breadcrumbs"/>
    </xsl:if>
  </xsl:template>

  <xsl:template name="user.header.navigation">
    <xsl:comment>#include virtual="&location-l3-template;"</xsl:comment>
  </xsl:template>

  <xsl:template name="user.footer.navigation">
    <xsl:comment>#include virtual="&location-frag-footer;"</xsl:comment>
  </xsl:template>

</xsl:stylesheet>
