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
        <kernel>/boot/kvm/vmlinuz-2.6.32-71.14.1.el6.x86_64</kernel>
        <initrd>/boot/kvm/initramfs-2.6.32-71.14.1.el6.x86_64.img</initrd>
        <cmdline>root=/dev/sda1 divider=10 notsc</cmdline>
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
      <serial type='pty'>
        <target port='0'/>
      </serial>
      <console type='pty'>
        <target port='0'/>
      </console>
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
  <xsl:template match="disk[@device = 'disk']">
    <disk type='block' device='disk'>
      <driver name='qemu' type='raw' />
      <xsl:apply-templates />
      <target dev='sda' bus='ide' />
      <address type='drive' controller='0' bus='0' unit='0' />
    </disk>
  </xsl:template>
</xsl:stylesheet>
