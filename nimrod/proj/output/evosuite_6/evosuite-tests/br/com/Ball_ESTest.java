/*
 * This file was automatically generated by EvoSuite
 * Wed Jun 05 16:57:44 GMT 2019
 */

package br.com;

import org.junit.Test;
import static org.junit.Assert.*;
import br.com.Ball;
import org.evosuite.runtime.EvoRunner;
import org.evosuite.runtime.EvoRunnerParameters;
import org.junit.runner.RunWith;

@RunWith(EvoRunner.class) @EvoRunnerParameters(mockJVMNonDeterminism = true, useVFS = true, useVNET = true, resetStaticState = true, separateClassLoader = true, useJEE = true) 
public class Ball_ESTest extends Ball_ESTest_scaffolding {

  @Test(timeout = 4000)
  public void test0()  throws Throwable  {
      Ball ball0 = new Ball((-1L), 0, 137, "", "", "z~jt-+P9b[e.-A#sE`#", "-VQ%", "GNW", "z~jt-+P9b[e.-A#sE`#", "z~jt-+P9b[e.-A#sE`#", "", "3BKB!");
      String string0 = ball0.finalString();
      assertEquals("KafkaSpoutConfig{kafkaProps=GNW, keyDeserializer=z~jt-+P9b[e.-A#sE`#, valueDeserializer=z~jt-+P9b[e.-A#sE`#, pollTimeoutMs=z~jt-+P9b[e.-A#sE`#, offsetCommitPeriodMs=-1, maxUncommittedOffsets=137, firstPollOffsetStrategy=, kafkaSpoutStreams=, tuplesBuilder=z~jt-+P9b[e.-A#sE`#, retryService=-VQ%, topics=, topicWildcardPattern=3BKB!}", string0); // (Primitive) Original Value: KafkaSpoutConfig{kafkaProps=GNW, keyDeserializer=z~jt-+P9b[e.-A#sE`#, valueDeserializer=z~jt-+P9b[e.-A#sE`#, pollTimeoutMs=z~jt-+P9b[e.-A#sE`#, offsetCommitPeriodMs=-1, maxUncommittedOffsets=137, firstPollOffsetStrategy=, kafkaSpoutStreams=, tuplesBuilder=z~jt-+P9b[e.-A#sE`#, retryService=-VQ%, topics=, topicWildcardPattern=3BKB!} | Regression Value: KafkaSpoutConfig{kafkaProps=GNW, keyDeserializer=z~jt-+P9b[e.-A#sE`#, valueDeserializer=z~jt-+P9b[e.-A#sE`#, pollTimeoutMs=z~jt-+P9b[e.-A#sE`#, offsetCommitPeriodMs=-1, maxRetries=0, maxUncommittedOffsets=137, firstPollOffsetStrategy=, kafkaSpoutStreams=, tuplesBuilder=z~jt-+P9b[e.-A#sE`#, retryService=-VQ%, topics=, topicWildcardPattern=3BKB!}
  }
}
