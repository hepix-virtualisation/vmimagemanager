<?xml version="1.0"?>

<!-- 
  DocBook-depend v0.1

  A Swiss-army knife for using DocBook with Makefiles.

  Paul Millar <p.millar@physics.gla.ac.uk>

  Please email me any updates!

  Some typical usages.  For each, there is a list of
  string-parameters that are needed for this XSLT.

  1. Simple lists

    a. all non-XML dependencies:

       <no parameters>

    b. all SVG dependencies:

       graphics = SVG

    c. all XML files:
       <not currently possible: needs an extra option>

  2. Define a variable FOO

    a. all non-XML depedencies:

       variable-name = FOO

    b. all SVG dependencies:

       variable-name = FOO
       graphics = SVG

    c. Define a variable FOO_PNG containing all PNG file
       dependencies from file foo.xml.  This is saved as
       file var-foo.dep, so include dependency for
       regenerating var-foo.dep

       variable-name = FOO_PNG
       graphics = PNG
       initial-file = foo.xml
       dep-file = var-foo.dep

  4. Generating Makefile dependencies

    a. DocBook will generate file foo-output.fo from foo.xml.
       Create a Makefile depedency for foo-output.fo.  The FO
       output uses SVG graphics only.

       output-file = foo-output.fo
       initial-file = foo.xml
       graphics = SVG

    b. DocBook will generate file foo.html from foo.xml.
       Include dependencies on PNG files as we want the
       build to fail if they're not there.  We save this as
       .foo.html.dep, so include dependencies on this file,
       too.

       output-file = foo.html
       initial-file = foo.xml
       graphics = PNG
       dep-file = .foo.html.dep

    c. DocBook output foo-info.5 is a manual page: it includes
       no graphics at all.

       output-file = foo-info.5
       initial-file = foo.xml
       graphics = none
       dep-file = .foo-info.5.dep
    
  Known issues:
    will repeat filenames if they are referenced more than once.
-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns:xi="http://www.w3.org/2001/XInclude"
		version="1.0">

  <xsl:param name="initial-file"/>
  <xsl:param name="output-file"/>
  <xsl:param name="dep-file"/>
  <xsl:param name="variable-name"/>
  <xsl:param name="graphics" select="'any'"/>

  <xsl:strip-space elements="*"/>
  <xsl:output method="text"/>

  <xsl:template match="/">

    <xsl:choose>
      <xsl:when test="boolean($output-file)">
	<xsl:value-of select="$output-file"/>
	<xsl:text>: </xsl:text>

	<xsl:value-of select="$initial-file"/>
      </xsl:when>

      <xsl:otherwise>
	<xsl:if test="boolean($variable-name)">
	  <xsl:value-of select="$variable-name"/>
	  <xsl:text> =</xsl:text>
	</xsl:if>

      </xsl:otherwise>
    </xsl:choose>

    <xsl:apply-templates mode="dependencies"/>

    <xsl:text>
</xsl:text>


    <xsl:if test="boolean($dep-file) and boolean($initial-file)">
      <xsl:value-of select="$dep-file"/>
      <xsl:text>: </xsl:text>
      <xsl:value-of select="$initial-file"/>
      
      <xsl:apply-templates mode="deps-dep"/>
      
      <xsl:text>
</xsl:text>
    </xsl:if>
  </xsl:template>


  <xsl:template match="/" mode="dependencies">
    <xsl:apply-templates mode="dependencies"/>    
  </xsl:template>

  <xsl:template match="/" mode="deps-dep">
    <xsl:apply-templates mode="deps-dep"/>
  </xsl:template>


  <!-- XInclude dependencies -->

  <xsl:template match="xi:include" mode="dependencies">
    <xsl:if test="boolean($output-file) or (boolean($initial-file) and $graphics = 'none')">
      <xsl:text> </xsl:text>
      <xsl:value-of select="@href"/>
    </xsl:if>

    <xsl:apply-templates select="document(@href)"
			 mode="dependencies"/>
  </xsl:template>


  <xsl:template match="xi:include" mode="deps-dep">
    <xsl:text> </xsl:text>
    <xsl:value-of select="@href"/>
    <xsl:apply-templates select="document(@href)"
			 mode="deps-dep"/>
  </xsl:template>


  <!-- DocBook dependencies -->

  <xsl:template match="imagedata" mode="dependencies">
    <xsl:choose>
      <xsl:when test="$graphics='any'">
	<xsl:text> </xsl:text>
	<xsl:value-of select="@fileref"/>
      </xsl:when>

      <xsl:when test="$graphics='none'">
      </xsl:when>

      <xsl:otherwise>
	<xsl:if test="@format=$graphics">
	  <xsl:text> </xsl:text>
	  <xsl:value-of select="@fileref"/>	  
	</xsl:if>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


  <!-- Ignore everything that's not an XML element -->

  <xsl:template match="text()|processing-instruction()|comment()" mode="dependencies"/>
  <xsl:template match="text()|processing-instruction()|comment()" mode="morefiles"/>
  <xsl:template match="text()|processing-instruction()|comment()" mode="deps-dep"/>


</xsl:stylesheet>
