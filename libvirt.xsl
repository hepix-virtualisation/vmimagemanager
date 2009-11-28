<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()" />
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="domain">
    <domain type="kvm">
      <os>
        <type arch="x86_64" machine="pc">hvm</type>
        <boot dev="hd" />
      </os>
      <features>
        <acpi />
        <apic />
        <pae />
      </features>
      <clock offset="utc" />
      <on_poweroff>destroy</on_poweroff>
      <on_reboot>destroy</on_reboot>
      <on_crash>destroy</on_crash>
      <xsl:apply-templates />
    </domain>
  </xsl:template>
  
  <xsl:template match="devices">
    <devices>
      <emulator>/usr/bin/kvm</emulator>
      <serial type="pty">
        <target port="0" />
      </serial>
      <console type="pty">
        <target port="0" />
      </console>
      <xsl:apply-templates />
    </devices>
  </xsl:template>
  
</xsl:stylesheet>
