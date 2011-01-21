<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="@*|node()">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()" />
    </xsl:copy>
  </xsl:template>
  <xsl:template match="domain">
    <domain type="kvm">
      <os>
        <type arch="x86_64" machine="pc">hvm</type>
        <kernel>/boot/kvm/vmlinuz-2.6.18-194.32.1.el5</kernel>
        <initrd>/boot/kvm/initrd-2.6.18-194.32.1.el5.img</initrd>
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
      <input type='mouse' bus='ps2' />
      <xsl:apply-templates />
      <graphics type='vnc' port='-1' autoport='yes'
      listen='127.0.0.1' keymap='en-us' />
    </devices>
  </xsl:template>

  <xsl:template match="interface[@type = 'bridge']">
    <interface type='bridge'>
      <xsl:apply-templates />
      <model type='virtio' />
      <address type='pci' domain='0x0000' bus='0x00' slot='0x03'
      function='0x0' />
    </interface>
  </xsl:template>

</xsl:stylesheet>
