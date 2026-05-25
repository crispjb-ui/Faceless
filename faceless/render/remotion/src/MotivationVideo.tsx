import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
} from 'remotion';

type Shot = {img: string; durationInFrames: number};
type Caption = {text: string; from: number; durationInFrames: number};

export type MotivationProps = {
  fps: number;
  shots: Shot[];
  captions: Caption[];
  voice: string;
  music: string | null;
};

export const calcMetadata = ({props}: {props: MotivationProps}) => {
  const total = props.shots.reduce((a, s) => a + s.durationInFrames, 0) || 1;
  return {durationInFrames: total, fps: props.fps || 30};
};

const KenBurns: React.FC<{src: string; durationInFrames: number}> = ({
  src,
  durationInFrames,
}) => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame, [0, durationInFrames], [1.05, 1.18], {
    extrapolateRight: 'clamp',
  });
  return (
    <AbsoluteFill>
      <Img
        src={staticFile(src)}
        style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${scale})`}}
      />
      <AbsoluteFill
        style={{background: 'linear-gradient(transparent 50%, rgba(0,0,0,0.9))'}}
      />
    </AbsoluteFill>
  );
};

const Caption: React.FC<{text: string}> = ({text}) => {
  const frame = useCurrentFrame();
  const pop = interpolate(frame, [0, 5], [0.85, 1], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center', padding: '0 70px 360px'}}>
      <p
        style={{
          color: 'white',
          fontFamily: 'Inter, Arial, sans-serif',
          fontWeight: 900,
          fontSize: 92,
          lineHeight: 1.1,
          textAlign: 'center',
          textTransform: 'uppercase',
          letterSpacing: 1,
          textShadow: '0 6px 28px rgba(0,0,0,0.95)',
          transform: `scale(${pop})`,
          margin: 0,
        }}
      >
        {text}
      </p>
    </AbsoluteFill>
  );
};

export const MotivationVideo: React.FC<MotivationProps> = ({shots, captions, voice, music}) => {
  let from = 0;
  return (
    <AbsoluteFill style={{backgroundColor: 'black'}}>
      {shots.map((shot, i) => {
        const seq = (
          <Sequence key={`s${i}`} from={from} durationInFrames={shot.durationInFrames}>
            <KenBurns src={shot.img} durationInFrames={shot.durationInFrames} />
          </Sequence>
        );
        from += shot.durationInFrames;
        return seq;
      })}
      {captions.map((c, i) => (
        <Sequence key={`c${i}`} from={c.from} durationInFrames={c.durationInFrames}>
          <Caption text={c.text} />
        </Sequence>
      ))}
      {voice ? <Audio src={staticFile(voice)} /> : null}
      {music ? <Audio src={staticFile(music)} volume={0.18} /> : null}
    </AbsoluteFill>
  );
};
