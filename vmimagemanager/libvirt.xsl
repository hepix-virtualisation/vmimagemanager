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
        <kernel>/boot/kvm/vmlinuz-i386-2.6.9-89.0.25.EL</kernel>
        <initrd>/boot/kvm/initrd-i386-2.6.9-89.0.25.EL.img</initrd>
        <cmdline>root=/dev/hda1 divider=10 notsc</cmdline>
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
      <input type='mouse' bus='ps2'/>      
      <xsl:apply-templates />
      <graphics type='vnc' port='-1' autoport='yes' listen='127.0.0.1' keymap='en-us'/>

    </devices>
  </xsl:template>
  
</xsl:stylesheet>
