#define __SAM3X8E__

#define BUFSIZE 0x400
#define BUFMASK 0x3FF

volatile int samples[BUFSIZE];
volatile int sptr = 0;
volatile int isr_count = 0;

void setup()
{
  SerialUSB.begin(500000);             // Use Native USB port for faster serial
  while (!SerialUSB);                  // Wait for USB serial connection

  adc_setup();                         // Setup ADC

  pmc_enable_periph_clk(TC_INTERFACE_ID + 0 * 3 + 0);  // Enable clock to TC0 channel 0

  TcChannel *t = &(TC0->TC_CHANNEL[0]);
  t->TC_CCR = TC_CCR_CLKDIS;
  t->TC_IDR = 0xFFFFFFFF;
  t->TC_SR;
  t->TC_CMR = TC_CMR_TCCLKS_TIMER_CLOCK1 |  // 42 MHz clock / 2
              TC_CMR_WAVE |
              TC_CMR_WAVSEL_UP_RC |
              TC_CMR_EEVT_XC0 |
              TC_CMR_ACPA_CLEAR | TC_CMR_ACPC_CLEAR |
              TC_CMR_BCPB_CLEAR | TC_CMR_BCPC_CLEAR;

  t->TC_RC = 875;     // 42 MHz / 875 = 48 kHz
  t->TC_RA = 440;     // 50% duty cycle
  t->TC_CMR = (t->TC_CMR & 0xFFF0FFFF) | TC_CMR_ACPA_CLEAR | TC_CMR_ACPC_SET;

  t->TC_CCR = TC_CCR_CLKEN | TC_CCR_SWTRG;

  setup_pio_TIOA0();  // Optional: drive pin 2 at 48kHz
  dac_setup();        // Optional: DAC triggered by timer
}

void setup_pio_TIOA0()
{
  PIOB->PIO_PDR = PIO_PB25B_TIOA0;
  PIOB->PIO_IDR = PIO_PB25B_TIOA0;
  PIOB->PIO_ABSR |= PIO_PB25B_TIOA0;
}

void dac_setup()
{
  pmc_enable_periph_clk(DACC_INTERFACE_ID);
  DACC->DACC_CR = DACC_CR_SWRST;

  DACC->DACC_MR =
    DACC_MR_TRGEN_EN | DACC_MR_TRGSEL(1) |
    (0 << DACC_MR_USER_SEL_Pos) |
    DACC_MR_REFRESH(0x0F) |
    (24 << DACC_MR_STARTUP_Pos);

  DACC->DACC_IDR = 0xFFFFFFFF;
  DACC->DACC_CHER = DACC_CHER_CH0;
}

void dac_write(int val)
{
  DACC->DACC_CDR = val & 0xFFF;
}

void adc_setup()
{
  NVIC_EnableIRQ(ADC_IRQn);
  ADC->ADC_IDR = 0xFFFFFFFF;
  ADC->ADC_IER = 0x80;              // EOC7 = channel A0
  ADC->ADC_CHDR = 0xFFFF;
  ADC->ADC_CHER = 0x80;             // Enable A0
  ADC->ADC_CGR = 0x15555555;
  ADC->ADC_COR = 0x00000000;

  ADC->ADC_MR = (ADC->ADC_MR & 0xFFFFFFF0) | (1 << 1) | ADC_MR_TRGEN;
}

#ifdef __cplusplus
extern "C"
{
#endif

void ADC_Handler(void)
{
  if (ADC->ADC_ISR & ADC_ISR_EOC7)
  {
    int val = *(ADC->ADC_CDR + 7);
    samples[sptr] = val;
    sptr = (sptr + 1) & BUFMASK;
    dac_write(0xFFF & ~val);  // Inverted to DAC
  }
  isr_count++;
}

#ifdef __cplusplus
}
#endif

void loop() {
  static int last = 0;
  while (last != sptr) {
    SerialUSB.println(samples[last]);
    last = (last + 1) & BUFMASK;
  }
}
