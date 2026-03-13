import Image from "next/image";
import clsx from "@/components/utils/clsx";
import { withBasePath } from "@/lib/base-path";

type PsyFlowLogoProps = {
  className?: string;
  imageClassName?: string;
  alt?: string;
  variant?: "black" | "white";
};

export function PsyFlowLogo({
  className,
  imageClassName,
  alt = "PsyFlow logo",
  variant = "black"
}: PsyFlowLogoProps) {
  const src =
    variant === "white"
      ? withBasePath("/images/branding/psyflow-logo-white.png")
      : withBasePath("/images/branding/psyflow-logo-black.png");

  return (
    <Image
      src={src}
      alt={alt}
      width={472}
      height={287}
      priority
      className={clsx("h-auto w-[150px] sm:w-[176px]", imageClassName, className)}
    />
  );
}

export function PsyFlowMark(props: PsyFlowLogoProps) {
  return <PsyFlowLogo {...props} />;
}
